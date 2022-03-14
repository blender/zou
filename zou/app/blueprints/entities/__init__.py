from flask import Blueprint
from zou.app.utils.api import configure_api_from_blueprint

from .resources import (
    EntityResource,
    EntitiesResource,
    AllEntitiesResource,
    EntitiesAndTasksResource,
    EntityPreviewsResource,
    EntityTaskTypesResource,
    EntityTasksResource,
    EntityVersionsResource,
    ProjectEntitiesResource,
    EpisodeEntitiesResource,
    EpisodeEntityTasksResource,
)

routes = [
    ("/data/entities", AllEntitiesResource),
    ("/data/entities/all", EntitiesResource),
    ("/data/entities/with-tasks", EntitiesAndTasksResource),
    ("/data/entities/<entity_id>", EntityResource),
    ("/data/entities/<entity_id>/task-types", EntityTaskTypesResource),
    ("/data/entities/<entity_id>/tasks", EntityTasksResource),
    ("/data/entities/<entity_id>/preview-files", EntityPreviewsResource),
    ("/data/entities/<entity_id>/versions", EntityVersionsResource),
    ("/data/episodes/<episode_id>/entities", EpisodeEntitiesResource),
    ("/data/episodes/<episode_id>/entity-tasks", EpisodeEntityTasksResource),
    ("/data/projects/<project_id>/entities", ProjectEntitiesResource),
]


blueprint = Blueprint("entities", "entities")
api = configure_api_from_blueprint(blueprint, routes)
