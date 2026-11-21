"""Convert database models into API responses."""

from app import storage
from app.captions.style import parse_style
from app.models import BrandKit, Clip, Project
from app.schemas.brand_kit import BrandKitOut
from app.schemas.clip import ClipOut, Framing
from app.schemas.project import ProjectDetail, ProjectSummary


def poster_path(project: Project) -> str | None:
    poster = storage.data_dir() / "projects" / project.id / "poster.jpg"
    return storage.relative(poster) if poster.exists() else None


def project_summary(project: Project) -> ProjectSummary:
    return ProjectSummary(
        id=project.id,
        title=project.title,
        source_type=project.source_type,
        source_url=project.source_url,
        status=project.status,
        progress=project.progress,
        error=project.error,
        duration=project.duration,
        poster_url=storage.media_url(poster_path(project)),
        clip_count=len(project.clips),
        created_at=project.created_at,
    )


def project_detail(project: Project) -> ProjectDetail:
    has_video = project.duration is not None and storage.source_video(project.id).exists()
    return ProjectDetail(
        **project_summary(project).model_dump(),
        width=project.width,
        height=project.height,
        fps=project.fps,
        language=project.language,
        settings=project.settings,
        video_url=storage.media_url(f"projects/{project.id}/source.mp4") if has_video else None,
        clips=[clip_out(clip) for clip in project.clips],
    )


def clip_out(clip: Clip) -> ClipOut:
    return ClipOut(
        id=clip.id,
        project_id=clip.project_id,
        rank=clip.rank,
        title=clip.title,
        reason=clip.reason,
        score=clip.score,
        start=clip.start,
        end=clip.end,
        words=clip.words,
        framing=Framing.model_validate(clip.framing or {}),
        style=parse_style(clip.style),
        thumbnail_url=storage.media_url(clip.thumbnail),
        render_status=clip.render_status,
        render_progress=clip.render_progress,
        render_error=clip.render_error,
        output_url=storage.media_url(clip.output),
    )


def brand_kit_out(kit: BrandKit) -> BrandKitOut:
    return BrandKitOut(
        id=kit.id,
        name=kit.name,
        is_default=kit.is_default,
        style=parse_style(kit.style),
        logo_url=storage.media_url(kit.logo),
        created_at=kit.created_at,
    )
