from rest_framework import viewsets, exceptions, status
from rest_framework.response import Response

from iron.api import serializers
from iron.models import DirectoryEntry


class File(viewsets.ViewSet):
    lookup_value_regex = '.*'
    lookup_field = 'path'
    serializer_class = serializers.DirectoryEntrySerializer

    def get_file(self, path):
        return Response({'file': path})

    def list(self, request):
        return self.retrieve(request)

    def retrieve(self, request, path=''):
        try:
            if path.endswith('/') or path == '':
                serializer = serializers.DirectoryEntrySerializer(
                    DirectoryEntry.ls(path),
                    many=True,
                    context={'request': request})
            else:
                entry = DirectoryEntry(path)
                serializer = serializers.DirectoryEntrySerializer(
                    entry,
                    context={'request': request})
                if entry.kind == DirectoryEntry.Kinds.DIRECTORY:
                    raise exceptions.NotFound()

            return Response(serializer.data)
        except FileNotFoundError as e:
            raise exceptions.NotFound("'{}' not found".format(path))

    def partial_update(self, request, path=''):
        try:
            entry = DirectoryEntry(path)
        except NotADirectoryError:
            raise exceptions.NotFound()
        serializer = serializers.DirectoryEntrySerializer(entry, data=request.data,
                                                          context={'request': request},
                                                          partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = {'Location': serializer.data['url']}
        return Response(serializer.data, status=status.HTTP_303_SEE_OTHER, headers=headers)

    def update(self, request, path=''):
        entry = DirectoryEntry(path)
        if path != '' and entry.kind == DirectoryEntry.Kinds.DIRECTORY:
            raise exceptions.MethodNotAllowed(request.method)

        serializer = serializers.DirectoryEntrySerializer(data=request.data,
                                                          context={'request': request,
                                                                   'path': path})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = serializers.DirectoryEntrySerializer(data=request.data,
                                                          context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = {'Location': serializer.data['url']}
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, path=''):
        try:
            recursive = request.query_params.get('recursive', 'False').lower() == 'true'
            DirectoryEntry.remove(path, recursive)
        except FileNotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
