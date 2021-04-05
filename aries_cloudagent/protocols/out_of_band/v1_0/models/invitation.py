"""Record for out of band invitations."""

from typing import Any

from marshmallow import fields

from .....core.profile import ProfileSession
from .....messaging.models.base_record import BaseExchangeRecord, BaseExchangeSchema
from .....messaging.valid import INDY_DID, UUIDFour


class InvitationRecord(BaseExchangeRecord):
    """Represents an out of band invitation record."""

    class Meta:
        """InvitationRecord metadata."""

        schema_class = "InvitationRecordSchema"

    RECORD_TYPE = "oob_invitation"
    RECORD_ID_NAME = "invitation_id"
    RECORD_TOPIC = "oob_invitation"
    TAG_NAMES = {"invi_msg_id", "public_did"}

    STATE_INITIAL = "initial"
    STATE_AWAIT_RESPONSE = "await_response"
    STATE_DONE = "done"

    def __init__(
        self,
        *,
        invitation_id: str = None,
        state: str = None,
        invi_msg_id: str = None,
        invitation: dict = None,  # serialized invitation message
        invitation_url: str = None,
        public_did: str = None,  # public DID in invitation; none if peer DID
        trace: bool = False,
        **kwargs,
    ):
        """Initialize a new InvitationRecord."""
        super().__init__(invitation_id, state, trace=trace, **kwargs)
        self._id = invitation_id
        self.state = state
        self.invi_msg_id = invi_msg_id
        self.invitation = invitation
        self.public_did = public_did
        self.invitation_url = invitation_url
        self.trace = trace

    @property
    def invitation_id(self) -> str:
        """Accessor for the ID associated with this exchange."""
        return self._id

    @property
    def record_value(self) -> dict:
        """Accessor for the JSON record value generated for this invitation."""
        return {
            prop: getattr(self, prop)
            for prop in (
                "invitation",
                "invitation_url",
                "state",
                "trace",
            )
        }

    @classmethod
    async def retrieve_by_public_did(cls, session: ProfileSession, public_did: str):
        """Retrieve by public DID."""
        cache_key = f"oob_invi_rec::{public_did}"
        record_id = await cls.get_cached_key(session, cache_key)
        if record_id:
            record = await cls.retrieve_by_id(session, record_id)
        else:
            record = await cls.retrieve_by_tag_filter(
                session=session,
                tag_filter={"public_did": public_did},
            )
            await cls.set_cached_key(session, cache_key, record.invitation_id)
        return record

    def __eq__(self, other: Any) -> bool:
        """Comparison between records."""
        return super().__eq__(other)


class InvitationRecordSchema(BaseExchangeSchema):
    """Schema to allow serialization/deserialization of invitation records."""

    class Meta:
        """InvitationRecordSchema metadata."""

        model_class = InvitationRecord

    invitation_id = fields.Str(
        required=False,
        description="Invitation record identifier",
        example=UUIDFour.EXAMPLE,
    )
    state = fields.Str(
        required=False,
        description="Out of band message exchange state",
        example=InvitationRecord.STATE_AWAIT_RESPONSE,
    )
    invi_msg_id = fields.Str(
        required=False,
        description="Invitation message identifier",
        example=UUIDFour.EXAMPLE,
    )
    invitation = fields.Dict(
        required=False,
        description="Out of band invitation object",
    )
    invitation_url = fields.Str(
        required=False,
        description="Invitation message URL",
        example=(
            "https://example.com/endpoint?"
            "c_i=eyJAdHlwZSI6ICIuLi4iLCAiLi4uIjogIi4uLiJ9XX0="
        ),
    )
    public_did = fields.Str(
        description="Public DID, if applicable", required=False, **INDY_DID
    )
