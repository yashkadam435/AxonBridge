# vault-policy.hcl
path "secret/data/axonbridge/*" {
  capabilities = ["read", "create", "update", "delete"]
}

path "secret/metadata/axonbridge/*" {
  capabilities = ["read", "delete", "list"]
}

path "transit/encrypt/axonbridge" {
  capabilities = ["update"]
}

path "transit/decrypt/axonbridge" {
  capabilities = ["update"]
}

path "transit/keys/axonbridge" {
  capabilities = ["read"]
}
