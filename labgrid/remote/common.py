from fnmatch import fnmatchcase

import attr


@attr.s
class ResourceEntry:
    data = attr.ib()  # cls, params
    acquired = attr.ib(default=None)

    def __attrs_post_init__(self):
        self.data.setdefault('avail', False)

    @property
    def avail(self):
        return self.data['avail']

    @property
    def cls(self):
        return self.data['cls']

    @property
    def params(self):
        return self.data['params']

    def asdict(self):
        return {
            'cls': self.cls,
            'params': self.params,
            'acquired': self.acquired,
            'avail': self.avail,
        }


@attr.s
class ResourceMatch:
    exporter = attr.ib()
    group = attr.ib()
    cls = attr.ib()
    name = attr.ib(default=None)

    @classmethod
    def fromstr(cls, pattern):
        if not (2 <= pattern.count("/") <= 3):
            raise ValueError(
                "invalid pattern format '{}' (use 'exporter/group/cls/name')".
                format(pattern)
            )
        return cls(*pattern.split("/"))

    def __str__(self):
        result = "{}/{}/{}".format(self.exporter, self.group, self.cls)
        if self.name is not None:
            result += "/{}".format(self.name)
        return result

    def ismatch(self, resource_path):
        exporter, group, cls, name = resource_path
        """Return True if this matches the given resource"""
        if not fnmatchcase(exporter, self.exporter):
            return False
        elif not fnmatchcase(group, self.group):
            return False
        elif not fnmatchcase(cls, self.cls):
            return False
        elif self.name and not fnmatchcase(name, self.name):
            return False
        else:
            return True


@attr.s
class Place:
    name = attr.ib()
    aliases = attr.ib(default=attr.Factory(set))
    comment = attr.ib(default="")
    matches = attr.ib(default=attr.Factory(list))
    acquired = attr.ib(default=None)
    acquired_resources = attr.ib(default=attr.Factory(list))

    def asdict(self):
        result = attr.asdict(self)
        del result['name']  # the name is the key in the places dict
        return result

    def show(self, level=0):
        indent = '  ' * level
        print(indent + "aliases: {}".format(', '.join(self.aliases)))
        print(indent + "comment: {}".format(self.comment))
        print(indent + "matches:")
        for match in self.matches:
            print(indent + "  {}".format(match))
        print(indent + "acquired: {}".format(self.acquired))
        print(indent + "acquired resources:")
        for resource in self.acquired_resources:
            print(indent + "  {}".format('/'.join(resource)))

    def hasmatch(self, resource_path):
        """Return True if this place as a ResourceMatch object for the given resource path.

        A resource_path has the structure (exporter, group, cls, name).
        """
        for match in self.matches:
            if match.ismatch(resource_path):
                return True
        return False
