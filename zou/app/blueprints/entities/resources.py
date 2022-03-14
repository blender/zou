from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from zou.app.services import (
    persons_service,
    projects_service,
    playlists_service,
    entities_service,
    tasks_service,
    user_service,
)

from zou.app.mixin import ArgsMixin
from zou.app.utils import permissions, query


class EntityResource(Resource, ArgsMixin):
    @jwt_required
    def get(self, entity_id):
        """
        Retrieve given entity.
        """
        entity = entities_service.get_full_entity(entity_id)
        if entity is None:
            entities_service.clear_entity_cache(entity_id)
            entity = entities_service.get_full_entity(entity_id)
        user_service.check_project_access(entity["project_id"])
        user_service.check_entity_access(entity["id"])
        return entity

    @jwt_required
    def delete(self, entity_id):
        """
        Delete given entity.
        """
        force = self.get_force()
        entity = entities_service.get_entity(entity_id)
        user_service.check_manager_project_access(entity["project_id"])
        entities_service.remove_entity(entity_id, force=force)
        return "", 204


class EntitiesResource(Resource):
    @jwt_required
    def get(self):
        """
        Retrieve all entity entries. Filters can be specified in the query string.
        """
        criterions = query.get_query_criterions_from_request(request)
        user_service.check_project_access(criterions.get("project_id", None))
        if permissions.has_vendor_permissions():
            criterions["assigned_to"] = persons_service.get_current_user()[
                "id"
            ]
        return entities_service.get_entities(criterions)


class AllEntitiesResource(Resource):
    @jwt_required
    def get(self):
        """
        Retrieve all entity entries. Filters can be specified in the query string.
        """
        criterions = query.get_query_criterions_from_request(request)
        if permissions.has_vendor_permissions():
            criterions["assigned_to"] = persons_service.get_current_user()[
                "id"
            ]
        user_service.check_project_access(criterions.get("project_id", None))
        return entities_service.get_entities(criterions)


class EntityTaskTypesResource(Resource):
    @jwt_required
    def get(self, entity_id):
        """
        Retrieve all task types related to a given entity.
        """
        entity = entities_service.get_entity(entity_id)
        user_service.check_project_access(entity["project_id"])
        user_service.check_entity_access(entity["id"])
        return tasks_service.get_task_types_for_entity(entity_id)


class EntityTasksResource(Resource, ArgsMixin):
    @jwt_required
    def get(self, entity_id):
        """
        Retrieve all tasks related to a given entity.
        """
        entity = entities_service.get_entity(entity_id)
        user_service.check_project_access(entity["project_id"])
        user_service.check_entity_access(entity["id"])
        relations = self.get_relations()
        return tasks_service.get_tasks_for_entity(entity_id, relations=relations)


class EpisodeEntityTasksResource(Resource, ArgsMixin):
    @jwt_required
    def get(self, episode_id):
        """
        Retrieve all tasks related to a given episode.
        """
        episode = entities_service.get_episode(episode_id)
        user_service.check_project_access(episode["project_id"])
        user_service.check_entity_access(episode["id"])
        if permissions.has_vendor_permissions():
            raise permissions.PermissionDenied
        relations = self.get_relations()
        return tasks_service.get_entity_tasks_for_episode(
            episode_id, relations=relations
        )


class EpisodeEntitiesResource(Resource, ArgsMixin):
    @jwt_required
    def get(self, episode_id):
        """
        Retrieve all entities related to a given episode.
        """
        episode = entities_service.get_episode(episode_id)
        user_service.check_project_access(episode["project_id"])
        user_service.check_entity_access(episode["id"])
        relations = self.get_relations()
        return entities_service.get_entities_for_episode(
            episode_id, relations=relations
        )


class EntityPreviewsResource(Resource):
    @jwt_required
    def get(self, entity_id):
        """
        Retrieve all previews related to a given entity. It sends them
        as a dict. Keys are related task type ids and values are arrays
        of preview for this task type.
        """
        entity = entities_service.get_entity(entity_id)
        user_service.check_project_access(entity["project_id"])
        user_service.check_entity_access(entity["id"])
        return playlists_service.get_preview_files_for_entity(entity_id)


class EntitiesAndTasksResource(Resource):
    @jwt_required
    def get(self):
        """
        Retrieve all entities, adds project name and all related tasks.
        """
        criterions = query.get_query_criterions_from_request(request)
        user_service.check_project_access(criterions.get("project_id", None))
        print(criterions)
        if permissions.has_vendor_permissions():
            criterions["assigned_to"] = persons_service.get_current_user()[
                "id"
            ]
        return entities_service.get_entities_and_tasks(criterions)


class ProjectEntitiesResource(Resource):
    @jwt_required
    def get(self, project_id):
        """
        Retrieve all entities related to a given project.
        """
        projects_service.get_project(project_id)
        user_service.check_project_access(project_id)
        return entities_service.get_entities_for_project(
            project_id, only_assigned=permissions.has_vendor_permissions()
        )

    @jwt_required
    def post(self, project_id):
        """
        Create a entity for given project.
        """
        (name, description, data, parent_id) = self.get_arguments()
        projects_service.get_project(project_id)
        user_service.check_manager_project_access(project_id)

        entity = entities_service.create_entity(
            project_id,
            name,
            data=data,
            description=description,
            parent_id=parent_id,
        )
        return entity, 201

    def get_arguments(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "name", help="The entity name is required.", required=True
        )
        parser.add_argument("description")
        parser.add_argument("data", type=dict)
        parser.add_argument("episode_id", default=None)
        args = parser.parse_args()
        return (
            args["name"],
            args.get("description", ""),
            args["data"],
            args["episode_id"],
        )


class EntityVersionsResource(Resource):
    """
    Retrieve data versions of given entity.
    """

    @jwt_required
    def get(self, entity_id):
        entity = entities_service.get_entity(entity_id)
        user_service.check_project_access(entity["project_id"])
        user_service.check_entity_access(entity["id"])
        return entities_service.get_entity_versions(entity_id)
