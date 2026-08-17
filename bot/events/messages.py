from bot.commands import handle_general_message, handle_team_message
from config import Settings
from services import AIMessageService, TeamService


def register_message_events(
    client,
    tree,
    settings: Settings,
    ai_service: AIMessageService,
    team_service: TeamService,
) -> None:
    @client.event
    async def on_member_join(member):
        for channel in member.guild.channels:
            if channel.name in {"一般", "這絕對不是幹話區"}:
                await ai_service.welcome(member, channel)

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if message.author.display_name == "傑哥KTV":
            return

        if not message.content:
            first_attachment = message.attachments[0] if message.attachments else None
            if not (
                first_attachment
                and first_attachment.content_type
                and first_attachment.content_type.startswith("image")
            ):
                return

        if await handle_general_message(message, client, tree, settings):
            return
        if await handle_team_message(message, team_service):
            return
        await ai_service.respond(message, client.user)
