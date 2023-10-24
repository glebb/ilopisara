from typing import Callable

import nextcord


class GameDetails(nextcord.ui.Select):
    def __init__(self, options, match_callback: Callable):
        self.match_callback = match_callback
        super().__init__(
            placeholder="Choose game to show details",
            options=options,
        )

    async def callback(self, interaction: nextcord.Interaction):
        await self.match_callback(interaction, self.values[0])


class DropdownView(nextcord.ui.View):
    def __init__(self, details, timeout):
        super().__init__(timeout=timeout)
        self.add_item(details)
