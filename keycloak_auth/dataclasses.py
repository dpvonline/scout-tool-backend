"""
Dataclasses for communication with keycloak
"""

from dataclasses import dataclass
from typing import List, Optional

from keycloak_auth.enums import Logic, PolicyType, DecisionStrategy


@dataclass
class RoleRepresentationComposites:
    realm: Optional[List[str]] = None


@dataclass
class RoleRepresentation:
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    composite: Optional[bool] = None
    composites: Optional[List[RoleRepresentationComposites]] = None
    clientRole: Optional[bool] = None
    containerId: Optional[str] = None
    attributes: Optional[List[str]] = None


@dataclass
class PolicyRoleRepresentation:
    id: Optional[str] = None
    required: Optional[bool] = None


@dataclass
class PolicyAggregateRepresentation:
    id: str


@dataclass
class PolicyBase:
    decisionStrategy: Optional[DecisionStrategy] = None
    logic: Optional[Logic] = None
    name: Optional[str] = None
    resources: Optional[List[str]] = None  # resources name
    type: Optional[PolicyType] = None
    owner: Optional[str] = None
    description: Optional[str] = None
    scopes: Optional[List[str]] = None
    id: Optional[str] = None
    config: Optional[dict] = None


@dataclass
class PolicyRole(PolicyBase):
    roles: Optional[List[PolicyRoleRepresentation]] = None


@dataclass
class PolicyAggregate(PolicyBase):
    policies: Optional[List[str]] = None


@dataclass
class PolicyUser(PolicyBase):
    users: Optional[List[str]] = None


@dataclass
class ResourceRepresentation:
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    ownerManagedAccess: Optional[bool] = None
    displayName: Optional[str] = None
    icon_uri: Optional[str] = None
    scopes: Optional[List['ScopeRepresentation']] = None
    uris: Optional[List[str]] = None


@dataclass
class ScopeRepresentation:
    displayName: Optional[str] = None
    iconUri: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    policies: Optional[List[PolicyBase]] = None
    resources: Optional[List[ResourceRepresentation]] = None


@dataclass
class ResourceServerRepresentation:
    clientId: Optional[str] = None
    decisionStrategy: Optional[DecisionStrategy] = None
    id: Optional[str] = None
    resources: Optional[List[ResourceRepresentation]] = None
    scopes: Optional[List[ScopeRepresentation]] = None


@dataclass
class ClientRepresentation:
    adminUrl: Optional[str] = None
    alwaysDisplayInConsole: Optional[bool] = None
    authorizationServicesEnabled: Optional[bool] = None
    authorizationSettings: Optional[ResourceServerRepresentation] = None
    baseUrl: Optional[str] = None
    bearerOnly: Optional[bool] = None
    clientAuthenticatorType: Optional[str] = None
    clientId: Optional[str] = None
    consentRequired: Optional[bool] = None
    defaultClientScopes: Optional[List[str]] = None
    description: Optional[str] = None
    directAccessGrantsEnabled: Optional[bool] = None
    enabled: Optional[bool] = None
    frontchannelLogout: Optional[bool] = None
    fullScopeAllowed: Optional[bool] = None
    id: Optional[str] = None
    implicitFlowEnabled: Optional[bool] = None
    name: Optional[str] = None
    nodeReRegistrationTimeout: Optional[int] = None
    notBefore: Optional[int] = None
    oauth2DeviceAuthorizationGrantEnabled: Optional[bool] = None
    optionalClientScopes: Optional[List[str]] = None
    origin: Optional[str] = None
    protocol: Optional[str] = None
    publicClient: Optional[bool] = None
    redirectUris: Optional[List[str]] = None
    registrationAccessToken: Optional[str] = None
    rootUrl: Optional[str] = None
    secret: Optional[str] = None
    serviceAccountsEnabled: Optional[bool] = None
    standardFlowEnabled: Optional[bool] = None
    surrogateAuthRequired: Optional[bool] = None
    webOrigins: Optional[List[str]] = None
