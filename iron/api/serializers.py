from rest_framework import exceptions, serializers

from iron import models


class DirectoryEntrySerializer(serializers.Serializer):
    path = serializers.CharField()
    url = serializers.HyperlinkedIdentityField(view_name='file-detail', lookup_field='path')
    size = serializers.IntegerField(read_only=True)
    mime_type = serializers.CharField(read_only=True)
    kind = serializers.ChoiceField(choices=models.DirectoryEntry.Kinds.as_choices())
    content = serializers.FileField(write_only=True, required=False)

    def validate(self, data):
        if self.instance:
            # doing a partial update
            if data.get('kind', None):
                raise exceptions.ValidationError({
                    'kind': 'Cannot update an entry type'
                })
            if data.get('content', None):
                raise exceptions.ValidationError({
                    'content': 'Cannot update content while renaming'
                })
        elif 'path' in self.context:
            # we are validating an in-place update (PUT request)
            if data.get('path') != self.context.get('path') and data.get('content', None):
                raise exceptions.ValidationError({
                    'path': "Cannot rename file while updating it's content"
                })

        if (data.get('kind', None) == models.DirectoryEntry.Kinds.DIRECTORY and
                data.get('content', None)):
            raise exceptions.ValidationError(
                {"content": "Cannot specify content while creating a directory"})
        return data

    def create(self, validated_data):
        try:
            if validated_data['kind'] == models.DirectoryEntry.Kinds.DIRECTORY:
                return models.DirectoryEntry.mkdir(validated_data['path'])
            if validated_data['kind'] == models.DirectoryEntry.Kinds.FILE:
                return models.DirectoryEntry.create_file(validated_data.get('path'),
                                                         validated_data.get('content', None))
        # ToDo: more granular exceptions
        except OSError as e:
            raise exceptions.ValidationError(
                {"non_fields_errors": ["Could not create: {}".format(validated_data['path'])]})

    def update(self, obj, validated_data):
        try:
            if 'path' in validated_data:
                obj.rename(validated_data.get('path'))
                return obj
            if 'content' in validated_data:
                obj.update_content(validated_data.get('content'))
                return obj
        # ToDo: more granular exceptions
        except OSError as e:
            raise exceptions.ValidationError(
                {"non_fields_errors": ["Could not update: {}".format(validated_data['path'])]})
