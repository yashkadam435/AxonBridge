"""
AxonBridge — User Service

User CRUD with password policy and role assignment.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.logging import get_logger
from app.core.security import hash_password, validate_password_strength, verify_password
from app.models.role import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

logger = get_logger(__name__)


class UserService:
    """User management service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, tenant_id: uuid.UUID, data: UserCreate, created_by: uuid.UUID | None = None
    ) -> User:
        """Create a new user with password validation."""
        # Check for duplicate email
        existing = await self.db.execute(
            select(User).where(User.email == data.email, User.is_deleted == False)  # noqa: E712
        )
        if existing.scalar_one_or_none():
            raise ConflictError(f"User with email '{data.email}' already exists")

        # Validate password strength
        errors = validate_password_strength(data.password)
        if errors:
            raise ValidationError(
                message="Password does not meet requirements",
                errors=[{"field": "password", "message": e} for e in errors],
            )

        user = User(
            tenant_id=tenant_id,
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            title=data.title,
            department=data.department,
            language_preference=data.language_preference,
            created_by=created_by,
            password_changed_at=datetime.now(UTC),
        )
        self.db.add(user)
        await self.db.flush()

        # Assign roles
        for role_id in data.role_ids:
            user_role = UserRole(user_id=user.id, role_id=role_id)
            self.db.add(user_role)

        await self.db.flush()
        logger.info("user_created", user_id=str(user.id), email=data.email)
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        """Get a user by ID."""
        stmt = select(User).where(User.id == user_id, User.is_deleted == False)  # noqa: E712
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User", str(user_id))
        return user

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        stmt = select(User).where(User.email == email, User.is_deleted == False)  # noqa: E712
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: uuid.UUID,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
    ) -> tuple[list[User], int]:
        """List users for a tenant with pagination and optional search."""
        stmt = select(User).where(
            User.tenant_id == tenant_id,
            User.is_deleted == False,  # noqa: E712
        )

        if search:
            stmt = stmt.where(
                (User.full_name.ilike(f"%{search}%"))
                | (User.email.ilike(f"%{search}%"))
            )

        # Count
        count_result = await self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = count_result.scalar() or 0

        # Paginate
        offset = (page - 1) * per_page
        stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(per_page)
        result = await self.db.execute(stmt)
        users = list(result.scalars().all())

        return users, total

    async def update(
        self, user_id: uuid.UUID, data: UserUpdate, updated_by: uuid.UUID | None = None
    ) -> User:
        """Update a user."""
        user = await self.get_by_id(user_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_by = updated_by
        await self.db.flush()
        logger.info("user_updated", user_id=str(user_id))
        return user

    async def change_password(
        self,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str,
    ) -> None:
        """Change a user's password."""
        user = await self.get_by_id(user_id)

        if not verify_password(current_password, user.hashed_password):
            raise ValidationError(message="Current password is incorrect")

        errors = validate_password_strength(new_password)
        if errors:
            raise ValidationError(
                message="New password does not meet requirements",
                errors=[{"field": "new_password", "message": e} for e in errors],
            )

        user.hashed_password = hash_password(new_password)
        user.password_changed_at = datetime.now(UTC)
        await self.db.flush()
        logger.info("password_changed", user_id=str(user_id))

    async def delete(self, user_id: uuid.UUID) -> None:
        """Soft delete a user."""
        user = await self.get_by_id(user_id)
        user.is_deleted = True
        user.is_active = False
        user.deleted_at = datetime.now(UTC)
        await self.db.flush()
        logger.info("user_deleted", user_id=str(user_id))
