# -*- coding: utf-8 -*-
import six


def _is_descriptor(obj):
    """Returns True if obj is a descriptor, False otherwise."""
    return (
            hasattr(obj, "__get__") or hasattr(obj, "__set__") or hasattr(obj, "__delete__")
    )


def _is_dunder(name):
    """Returns True if a __dunder__ name, False otherwise."""
    return (
            name[:2] == name[-2:] == "__"
            and name[2:3] != "_"
            and name[-3:-2] != "_"
            and len(name) > 4
    )


def _is_sunder(name):
    """Returns True if a _sunder_ name, False otherwise."""
    return (
            name[0] == name[-1] == "_"
            and name[1:2] != "_"
            and name[-2:-1] != "_"
            and len(name) > 2
    )


# until EnumMeta finishes running the first time the Enum class doesn't exist.
Enum = None


class _EnumDict(dict):
    """Track enum member order and ensure member names are not reused.

    EnumMeta will use the names found in self._member_names as the
    enumeration member names.

    """

    def _check_value_type(self, v):
        """The value type must be six.integer_types or six.string_types

        In fact, enumeration does not concern about values,
        but just the names of enumeration.

        Value type are restricted for the convenience to be json serializable.

        """

        def _check_basetype(v):
            if not isinstance(v, self._allow_types):
                raise TypeError(
                    "Value type must be one of [%s], "
                    "instead of %s" % (", ".join(map(str, self._allow_types)), type(v))
                )

        if type(v) is tuple:
            if len(v) != 2:
                raise TypeError("Tuple enum definition must be length of 2")
            _check_basetype(v[0])
            if not isinstance(v[1], six.string_types):
                raise TypeError(
                    "The second element of tuple enum definition "
                    "must be string, i.e. an explanation of the enum value"
                )
        else:
            _check_basetype(v)

    def __init__(self, allow_types):
        super(_EnumDict, self).__init__()
        self._member_names = []
        self._allow_types = allow_types

    def __setitem__(self, key, value):
        """Changes anything not dundered

        If an enum member name is used twice, an error is raised; duplicate
        values are not checked for.

        Single underscore (sunder) names are reserved.

        """
        if _is_sunder(key):
            raise ValueError("_names_ are reserved for future Enum use")
        elif _is_dunder(key):
            pass
        elif key in self._member_names:
            # descriptor overwriting an enum?
            raise TypeError("Attempted to reuse key: %r" % key)
        elif not _is_descriptor(value):
            if key in self:
                # enum overwriting a descriptor?
                raise TypeError("Key already defined as: %r" % self[key])
            # value must be BASE_TYPE, or tuple of (BASE_TYPE, six.string_types)
            # BASE_TYPE is six.string_types or integer
            self._check_value_type(value)
            self._member_names.append(key)
        super(_EnumDict, self).__setitem__(key, value)


class EnumMeta(type):
    """Metaclass for Enum"""

    @staticmethod
    def _find_allow_types_(cls, bases):
        all_types = set(six.integer_types) | {six.text_type, str}
        allow_types = set()
        if Enum is None:  # Enum base class
            assert cls == "Enum"
            return tuple(all_types)
        else:
            for base in bases:
                if not issubclass(base, Enum):
                    allow_types.add(base)
        if allow_types:
            return tuple(all_types & allow_types)
        else:
            return tuple(all_types)

    @classmethod
    def __prepare__(mcs, cls, bases):
        return _EnumDict(EnumMeta._find_allow_types_(cls, bases))

    def __new__(mcs, cls, bases, _dct):
        # hacking to generate an _EnumDict Object
        dct = _dct

        # save enum items into separate mapping so they don't get baked into the new class
        members = dict([(k, dct[k]) for k in dct._member_names])
        for name in dct._member_names:
            del dct[name]

        # check for illegal enum names (any others?)
        invalid_names = set(members) & {
            "mro",
        }
        if invalid_names:
            raise ValueError(
                "Invalid enum member name: {0}".format(",".join(invalid_names))
            )

        # create our new Enum type
        enum_class = super(EnumMeta, mcs).__new__(mcs, cls, bases, dct)
        enum_class._member_names_ = []  # names in definition order
        enum_class._member_map_ = dict()  # name->value map

        # Reverse value->name map for hashable values.
        enum_class._value2member_map_ = {}
        enum_class.enum_dict = {}
        enum_class._value2name_map_ = {}
        enum_class._name_map_ = {}
        enum_class.choices = []

        # instantiate them, checking for duplicates as we go
        # we instantiate first instead of checking for duplicates first in case
        # a custom __new__ is doing something funky with the values -- such as
        # auto-numbering ;)
        for member_name, value in six.iteritems(members):
            if isinstance(value, tuple):
                real_value = value[0]
                desc = value[1]
            else:
                real_value = value
                desc = ""
            enum_member = enum_class()
            enum_member._name_ = member_name
            enum_member._value_ = real_value
            enum_member._desc_ = desc
            # If another member with the same value was already defined, the
            # new member becomes an alias to the existing one.
            for name, canonical_member in six.iteritems(enum_class._member_map_):
                if canonical_member._value_ == enum_member._value_:
                    enum_member = canonical_member
                    break
            else:
                # Aliases don't appear in member names (only in __members__).
                enum_class._member_names_.append(member_name)
            # now add to _member_map_
            enum_class._member_map_[member_name] = enum_member
            enum_class._value2member_map_[real_value] = enum_member
            enum_class._value2name_map_[real_value] = member_name
            enum_class._name_map_[member_name] = real_value
            enum_class.enum_dict[real_value] = desc
            enum_class.choices.append([real_value, desc])

        return enum_class

    def __contains__(cls, value):
        return value in cls._value2member_map_

    def __delattr__(cls, attr):
        if attr in cls._member_map_:
            raise AttributeError("%s: cannot delete Enum member." % cls.__name__)
        super(EnumMeta, cls).__delattr__(attr)

    def __getattr__(cls, name):
        """Return the enum member matching `name`

        We use __getattr__ instead of descriptors or inserting into the enum
        class' __dict__ in order to support `name` and `value` being both
        properties for enum members (which live in the class' __dict__) and
        enum members themselves.

        """
        # check if classmethod(bound now)
        if _is_dunder(name):
            raise AttributeError(name)
        try:
            enum_member = cls._member_map_[name]
            return enum_member._value_
        except KeyError:
            six.raise_from(AttributeError(name), None)

    def __desc__(cls, value):
        return cls._value2member_map_[value]._desc_

    def _name_(cls, value):
        return cls._value2name_map_[value]

    @property
    def __members__(cls):
        """Returns a mapping of member name->value.

        This mapping lists all enum members, including aliases. Note that this
        is a read-only view of the internal mapping.

        """
        return cls._member_map_.copy()

    @property
    def __map__(cls):
        return cls._name_map_.copy()

    def __getitem__(cls, name):
        return cls._member_map_[name]

    def __iter__(cls):
        """Returns a tuple of tuples(member.value, member.desc) for each member"""
        return (
            (cls._member_map_[name]._value_, cls._member_map_[name]._desc_)
            for name in cls._member_names_
        )

    def __len__(cls):
        return len(cls._member_names_)

    def __repr__(cls):
        return "<enum %r>" % cls.__name__

    def __reversed__(cls):
        return (cls._member_map_[name] for name in reversed(cls._member_names_))

    def __setattr__(cls, name, value):
        """Block attempts to reassign Enum members.

        A simple assignment to the class namespace only changes one of the
        several possible ways to get an Enum member from the Enum class,
        resulting in an inconsistent Enumeration.

        """
        member_map = cls.__dict__.get("_member_map_", {})
        if name in member_map:
            raise AttributeError("Cannot reassign members.")
        super(EnumMeta, cls).__setattr__(name, value)

    def __dir__(self):
        return list(super(EnumMeta, self).__dir__()) + self._member_names_


class Enum(metaclass=EnumMeta):
    """Generic enumeration.

    Derive from this class to define new enumerations.

    """

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, self._desc_)

    def __str__(self):
        return f"{self._desc_}"

    @classmethod
    def get_desc(cls, key, default_value=None):
        """
        获取枚举描述信息
        """
        try:
            return cls.__desc__(key)
        except KeyError:
            return default_value

    @classmethod
    def get_name(cls, key, default_value=None):
        """
        获取枚举定义名称信息
        """
        try:
            return cls._name_(key)
        except KeyError:
            return default_value

    @classmethod
    def to_dict(cls, default_value=None):
        """
        返回枚举类型字典
        """
        try:
            return cls.enum_dict
        except KeyError:
            return default_value

    @classmethod
    def member_map(cls, default_value=None):
        """
        返回枚举映射
        """
        try:
            return cls._member_map_
        except KeyError:
            return default_value


def unique(enumeration):
    """
    Class decorator for enumerations ensuring unique member values.
    do not define another same value to two different names.
    """
    duplicates = []
    for name, member in six.iteritems(enumeration.__members__):
        if name != member._name_:
            duplicates.append((name, member._name_))
    if duplicates:
        alias_details = ", ".join(
            ["%s -> %s" % (alias, name) for (alias, name) in duplicates]
        )
        raise ValueError(
            "duplicate values found in %r: %s" % (enumeration, alias_details)
        )
    return enumeration


if __name__ == "__main__":
    @unique
    class DEMO(Enum):
        """
        for example
        eg:
        备注name = (枚举类型, 描述信息)
        """

        TEST1 = (1, "测试属性1")
        TEST2 = (2, "测试属性2")


    print(DEMO.get_desc(DEMO.TEST1))  # 获取枚举描述信息
    print(DEMO().to_dict())  # 转换dict
    print(dict(DEMO))  # 同上
    print(DEMO.TEST1)  # 取枚举类型
    print(DEMO().member_map())  # 取枚举成员映射
    print(DEMO.__doc__)  # 获取枚举类备注信息
    print(DEMO.get_name(DEMO.TEST1))  # 获取枚举类型标注名称
    print(DEMO.__map__)  # 获取name value map
    print(DEMO.__members__)  # 得到属性对象映射
    print(DEMO.__members__.get("TEST1"))  # str 反射 desc
