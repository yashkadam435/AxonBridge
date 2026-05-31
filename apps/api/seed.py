import asyncio
from app.core.database import get_managed_session
from app.models.tenant import Tenant
from app.models.user import User
from app.core.security import hash_password
from datetime import datetime, UTC

async def seed():
    async with get_managed_session() as session:
        # Create Tenant
        tenant = Tenant(
            name="AxonBridge Demo Hospital",
            slug="demo-hospital",
            description="Demo environment for AxonBridge",
            subscription_tier="enterprise",
            compliance_region="us",
            is_active=True
        )
        session.add(tenant)
        await session.flush()

        # Create Admin User
        admin = User(
            tenant_id=tenant.id,
            email="admin@axonbridge.io",
            full_name="System Administrator",
            hashed_password=hash_password("AxonBridge2026!"),
            is_active=True,
            mfa_enabled=False,
            password_changed_at=datetime.now(UTC),
            language_preference="en",
            theme_preference="system"
        )
        session.add(admin)
        
        print("Successfully created tenant and admin user.")
        print("Email: admin@axonbridge.io")
        print("Password: AxonBridge2026!")

if __name__ == "__main__":
    asyncio.run(seed())
