from ..schemas import ComicOutline, ComicStory, ComicPanelLayout


def build_comic_layout(outline: ComicOutline, story: ComicStory, image_paths: list[str]) -> list[ComicPanelLayout]:
    if not (len(outline.panels) == len(story.panels) == len(image_paths)):
        raise ValueError("Outline, story, and image counts must match.")

    layout = []
    for outline_panel, story_panel, image_path in zip(outline.panels, story.panels, image_paths):
        if outline_panel.panel_number != story_panel.panel_number:
            raise ValueError("Panel numbering mismatch between outline and story.")
        layout.append(
            ComicPanelLayout(
                panel_number=outline_panel.panel_number,
                title=outline_panel.title,
                image_path=image_path,
                scene_description=outline_panel.scene_description,
                caption=story_panel.caption,
                narration=story_panel.narration,
                dialogue=story_panel.dialogue,
                image_prompt=outline_panel.image_prompt,
            )
        )
    return layout
