from models.model import Model


class Config(Model):
    guild_id: int
    polls_channel_id: int

    @classmethod
    async def get(cls, guild_id: int):
        query = """SELECT * FROM config
                    WHERE guild_id = $1"""
        return await cls.fetchrow(query, guild_id)
