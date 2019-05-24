#include "../../third_party/command_line_tools/source/dat.hpp"
#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

/// count determines the number of events in the given stream.
template <sepia::type event_stream_type>
npy_intp count(std::unique_ptr<std::istream> stream) {
    npy_intp size = 0;
    sepia::join_observable<event_stream_type>(std::move(stream), [&](sepia::event<event_stream_type>) { ++size; });
    return size;
}

/// description represents a named type with an offset.
struct description {
    std::string name;
    NPY_TYPES type;
};

/// descriptions returns the fields names, scalar types and offsets associated with an event type.
template <sepia::type event_stream_type>
std::vector<description> get_descriptions();
template <>
std::vector<description> get_descriptions<sepia::type::generic>() {
    return {{"t", NPY_UINT64}, {"bytes", NPY_OBJECT}};
}
template <>
std::vector<description> get_descriptions<sepia::type::dvs>() {
    return {{"t", NPY_UINT64}, {"x", NPY_UINT16}, {"y", NPY_UINT16}, {"is_increase", NPY_BOOL}};
}
template <>
std::vector<description> get_descriptions<sepia::type::atis>() {
    return {{"t", NPY_UINT64},
            {"x", NPY_UINT16},
            {"y", NPY_UINT16},
            {"is_threshold_crossing", NPY_BOOL},
            {"polarity", NPY_BOOL}};
}
template <>
std::vector<description> get_descriptions<sepia::type::color>() {
    return {
        {"t", NPY_UINT64}, {"x", NPY_UINT16}, {"y", NPY_UINT16}, {"r", NPY_UINT8}, {"g", NPY_UINT8}, {"b", NPY_UINT8}};
}

/// offsets calculates the packed offsets from the description types.
template <sepia::type event_stream_type>
std::vector<uint8_t> get_offsets() {
    auto descriptions = get_descriptions<event_stream_type>();
    std::vector<uint8_t> offsets(descriptions.size(), 0);
    for (std::size_t index = 1; index < descriptions.size(); ++index) {
        switch (descriptions[index - 1].type) {
            case NPY_BOOL:
            case NPY_UINT8:
                offsets[index] = offsets[index - 1] + 1;
                break;
            case NPY_UINT16:
                offsets[index] = offsets[index - 1] + 2;
                break;
            case NPY_UINT64:
                offsets[index] = offsets[index - 1] + 8;
                break;
            default:
                throw std::runtime_error("unknown type for offset calculation");
        }
    }
    return offsets;
}

/// stream_to_array returns a structured array with the required length to accomodate the given stream.
template <sepia::type event_stream_type>
PyArrayObject* stream_to_array(npy_intp size) {
    const auto descriptions = get_descriptions<event_stream_type>();
    auto python_names_and_types = PyList_New(static_cast<Py_ssize_t>(descriptions.size()));
    for (Py_ssize_t index = 0; index < static_cast<Py_ssize_t>(descriptions.size()); ++index) {
        if (PyList_SetItem(
                python_names_and_types,
                index,
                PyTuple_Pack(
                    2,
                    PyUnicode_FromString(descriptions[index].name.c_str()),
                    PyArray_TypeObjectFromType(descriptions[index].type)))
            < 0) {
            throw std::runtime_error("PyList_SetItem failed");
        }
    }
    PyArray_Descr* dtype;
    if (PyArray_DescrConverter(python_names_and_types, &dtype) == NPY_FAIL) {
        throw std::runtime_error("PyArray_DescrConverter failed");
    }
    return reinterpret_cast<PyArrayObject*>(
        PyArray_NewFromDescr(&PyArray_Type, dtype, 1, &size, nullptr, nullptr, 0, nullptr));
}
template <sepia::type event_stream_type>
PyArrayObject* stream_to_array(std::unique_ptr<std::istream> stream) {
    return stream_to_array<event_stream_type>(count<event_stream_type>(std::move(stream)));
}

/// read_event_stream loads events from an Event Stream file.
static PyObject* read_event_stream(PyObject* self, PyObject* args) {
    const char* filename_as_char_array;
    if (!PyArg_ParseTuple(args, "s", &filename_as_char_array)) {
        return nullptr;
    }
    auto stream = PyDict_New();
    try {
        const std::string filename(filename_as_char_array);
        const auto header = sepia::read_header(sepia::filename_to_ifstream(filename));
        switch (header.event_stream_type) {
            case sepia::type::generic: {
                auto events = stream_to_array<sepia::type::generic>(sepia::filename_to_ifstream(filename));
                const auto offsets = get_offsets<sepia::type::generic>();
                npy_intp index = 0;
                sepia::join_observable<sepia::type::generic>(
                    sepia::filename_to_ifstream(filename), [&](sepia::generic_event generic_event) {
                        auto payload = reinterpret_cast<uint8_t*>(PyArray_GETPTR1(events, index));
                        *reinterpret_cast<uint64_t*>(payload + offsets[0]) = generic_event.t;
                        *reinterpret_cast<PyObject**>(payload + offsets[1]) = PyBytes_FromStringAndSize(
                            reinterpret_cast<const char*>(generic_event.bytes.data()), generic_event.bytes.size());
                        ++index;
                    });
                PyDict_SetItem(stream, PyUnicode_FromString("type"), PyUnicode_FromString("generic"));
                PyDict_SetItem(stream, PyUnicode_FromString("events"), reinterpret_cast<PyObject*>(events));
                break;
            }
            case sepia::type::dvs: {
                auto events = stream_to_array<sepia::type::dvs>(sepia::filename_to_ifstream(filename));
                const auto offsets = get_offsets<sepia::type::dvs>();
                npy_intp index = 0;
                sepia::join_observable<sepia::type::dvs>(
                    sepia::filename_to_ifstream(filename), [&](sepia::dvs_event dvs_event) {
                        auto payload = reinterpret_cast<uint8_t*>(PyArray_GETPTR1(events, index));
                        *reinterpret_cast<uint64_t*>(payload + offsets[0]) = dvs_event.t;
                        *reinterpret_cast<uint16_t*>(payload + offsets[1]) = dvs_event.x;
                        *reinterpret_cast<uint16_t*>(payload + offsets[2]) = dvs_event.y;
                        *reinterpret_cast<bool*>(payload + offsets[3]) = dvs_event.is_increase;
                        ++index;
                    });
                PyDict_SetItem(stream, PyUnicode_FromString("type"), PyUnicode_FromString("dvs"));
                PyDict_SetItem(stream, PyUnicode_FromString("width"), PyLong_FromUnsignedLong(header.width));
                PyDict_SetItem(stream, PyUnicode_FromString("height"), PyLong_FromUnsignedLong(header.height));
                PyDict_SetItem(stream, PyUnicode_FromString("events"), reinterpret_cast<PyObject*>(events));
                break;
            }
            case sepia::type::atis: {
                auto events = stream_to_array<sepia::type::atis>(sepia::filename_to_ifstream(filename));
                const auto offsets = get_offsets<sepia::type::atis>();
                npy_intp index = 0;
                sepia::join_observable<sepia::type::atis>(
                    sepia::filename_to_ifstream(filename), [&](sepia::atis_event atis_event) {
                        auto payload = reinterpret_cast<uint8_t*>(PyArray_GETPTR1(events, index));
                        *reinterpret_cast<uint64_t*>(payload + offsets[0]) = atis_event.t;
                        *reinterpret_cast<uint16_t*>(payload + offsets[1]) = atis_event.x;
                        *reinterpret_cast<uint16_t*>(payload + offsets[2]) = atis_event.y;
                        *reinterpret_cast<bool*>(payload + offsets[3]) = atis_event.is_threshold_crossing;
                        *reinterpret_cast<bool*>(payload + offsets[4]) = atis_event.polarity;
                        ++index;
                    });
                PyDict_SetItem(stream, PyUnicode_FromString("type"), PyUnicode_FromString("atis"));
                PyDict_SetItem(stream, PyUnicode_FromString("width"), PyLong_FromUnsignedLong(header.width));
                PyDict_SetItem(stream, PyUnicode_FromString("height"), PyLong_FromUnsignedLong(header.height));
                PyDict_SetItem(stream, PyUnicode_FromString("events"), reinterpret_cast<PyObject*>(events));
                break;
            }
            case sepia::type::color: {
                auto events = stream_to_array<sepia::type::color>(sepia::filename_to_ifstream(filename));
                const auto offsets = get_offsets<sepia::type::color>();
                npy_intp index = 0;
                sepia::join_observable<sepia::type::color>(
                    sepia::filename_to_ifstream(filename), [&](sepia::color_event color_event) {
                        auto payload = reinterpret_cast<uint8_t*>(PyArray_GETPTR1(events, index));
                        *reinterpret_cast<uint64_t*>(payload + offsets[0]) = color_event.t;
                        *reinterpret_cast<uint16_t*>(payload + offsets[1]) = color_event.x;
                        *reinterpret_cast<uint16_t*>(payload + offsets[2]) = color_event.y;
                        *reinterpret_cast<uint8_t*>(payload + offsets[3]) = color_event.r;
                        *reinterpret_cast<uint8_t*>(payload + offsets[4]) = color_event.g;
                        *reinterpret_cast<uint8_t*>(payload + offsets[5]) = color_event.b;
                        ++index;
                    });
                PyDict_SetItem(stream, PyUnicode_FromString("type"), PyUnicode_FromString("color"));
                PyDict_SetItem(stream, PyUnicode_FromString("width"), PyLong_FromUnsignedLong(header.width));
                PyDict_SetItem(stream, PyUnicode_FromString("height"), PyLong_FromUnsignedLong(header.height));
                PyDict_SetItem(stream, PyUnicode_FromString("events"), reinterpret_cast<PyObject*>(events));
                break;
            }
            default:
                break;
        }
    } catch (const std::runtime_error& exception) {
        PyErr_SetString(PyExc_RuntimeError, exception.what());
        stream = nullptr;
    }
    return stream;
}

/// get_width_and_height loads the width and height keys from a dict.
static std::pair<uint16_t, uint16_t> get_width_and_height(PyObject* dict) {
    std::pair<uint16_t, uint16_t> width_and_height;
    auto width = PyDict_GetItem(dict, PyUnicode_FromString("width"));
    if (!width) {
        throw std::runtime_error("the stream dict must have a 'width' key");
    }
    if (!PyLong_Check(width)) {
        throw std::runtime_error("'width' must be a long integer");
    }
    const auto width_as_long = PyLong_AsLong(width);
    width_and_height.first = static_cast<uint16_t>(width_as_long);
    if (width_and_height.first != width_as_long) {
        throw std::runtime_error("'width' must be in the range [0, 65535]");
    }
    auto height = PyDict_GetItem(dict, PyUnicode_FromString("height"));
    if (!height) {
        throw std::runtime_error("the dict must have a 'height' key");
    }
    if (!PyLong_Check(height)) {
        throw std::runtime_error("'height' must be a long integer");
    }
    const auto height_as_long = PyLong_AsLong(height);
    width_and_height.second = static_cast<uint16_t>(height_as_long);
    if (width_and_height.second != height_as_long) {
        throw std::runtime_error("'height' must be in the range [0, 65535]");
    }
    return width_and_height;
}

/// get_events loads the 'events' key from a dict.
template <sepia::type event_stream_type>
PyArrayObject* get_events(PyObject* dict) {
    auto object = PyDict_GetItem(dict, PyUnicode_FromString("events"));
    if (!object) {
        throw std::runtime_error("the stream dict must have an 'events' key");
    }
    if (!PyArray_Check(object)) {
        throw std::runtime_error("'events' must be a numpy array");
    }
    auto events = reinterpret_cast<PyArrayObject*>(object);
    if (PyArray_NDIM(events) != 1) {
        throw std::runtime_error("'events' must have a single dimension");
    }
    const auto descriptions = get_descriptions<event_stream_type>();
    const auto offsets = get_offsets<event_stream_type>();
    auto fields = PyArray_DESCR(events)->fields;
    if (!PyMapping_Check(fields)) {
        throw std::runtime_error("'events' must be a structured array");
    }
    for (Py_ssize_t index = 0; index < static_cast<Py_ssize_t>(descriptions.size()); ++index) {
        auto field = PyMapping_GetItemString(fields, descriptions[index].name.c_str());
        if (!field) {
            throw std::runtime_error(
                std::string("'events' must be a structured array with a '") + descriptions[index].name + "' field");
        }
        if (reinterpret_cast<PyArray_Descr*>(PyTuple_GetItem(field, 0))->type_num != descriptions[index].type) {
            throw std::runtime_error(
                std::string("the field '") + descriptions[index].name + " of 'events' must have the type "
                + std::to_string(descriptions[index].type));
        }
        if (PyLong_AsLong(PyTuple_GetItem(field, 1)) != offsets[index]) {
            throw std::runtime_error(
                std::string("the field '") + descriptions[index].name + " of 'events' must have the offset "
                + std::to_string(offsets[index]));
        }
    }
    return events;
}

/// write_event_stream stores events to an Event Stream file.
static PyObject* write_event_stream(PyObject* self, PyObject* args) {
    PyObject* stream;
    const char* filename_as_char_array;
    if (!PyArg_ParseTuple(args, "O!s", &PyDict_Type, &stream, &filename_as_char_array)) {
        return nullptr;
    }
    try {
        auto type = PyDict_GetItem(stream, PyUnicode_FromString("type"));
        if (!type) {
            throw std::runtime_error("the dict must have a 'type' key");
        }
        if (!PyUnicode_Check(type)) {
            throw std::runtime_error("'type' must be a unicode string");
        }
        auto type_as_python_string = PyUnicode_AsEncodedString(type, "utf-8", "strict");
        const std::string type_as_string(PyBytes_AsString(type_as_python_string));
        Py_DECREF(type_as_python_string);
        if (type_as_string == "generic") {
            const auto events = get_events<sepia::type::generic>(stream);
            const auto offsets = get_offsets<sepia::type::generic>();
            sepia::write<sepia::type::generic> write(sepia::filename_to_ofstream(std::string(filename_as_char_array)));
            for (npy_intp index = 0; index < PyArray_SIZE(events); ++index) {
                auto payload = reinterpret_cast<uint8_t*>(PyArray_GETPTR1(events, index));
                auto bytes = *reinterpret_cast<PyObject**>(payload + offsets[1]);
                if (!PyBytes_Check(bytes)) {
                    throw std::runtime_error("'bytes' elements of 'events' must be byte strings");
                }
                std::string bytes_as_string(PyBytes_AsString(bytes));
                write({*reinterpret_cast<uint64_t*>(payload + offsets[0]),
                       std::vector<uint8_t>(bytes_as_string.begin(), bytes_as_string.end())});
            }
        } else if (type_as_string == "dvs") {
            const auto width_and_height = get_width_and_height(stream);
            const auto events = get_events<sepia::type::dvs>(stream);
            const auto offsets = get_offsets<sepia::type::dvs>();
            sepia::write<sepia::type::dvs> write(
                sepia::filename_to_ofstream(std::string(filename_as_char_array)),
                width_and_height.first,
                width_and_height.second);
            for (npy_intp index = 0; index < PyArray_SIZE(events); ++index) {
                auto payload = reinterpret_cast<uint8_t*>(PyArray_GETPTR1(events, index));
                write({*reinterpret_cast<uint64_t*>(payload + offsets[0]),
                       *reinterpret_cast<uint16_t*>(payload + offsets[1]),
                       *reinterpret_cast<uint16_t*>(payload + offsets[2]),
                       *reinterpret_cast<bool*>(payload + offsets[3])});
            }
        } else if (type_as_string == "atis") {
            const auto width_and_height = get_width_and_height(stream);
            const auto events = get_events<sepia::type::atis>(stream);
            const auto offsets = get_offsets<sepia::type::atis>();
            sepia::write<sepia::type::atis> write(
                sepia::filename_to_ofstream(std::string(filename_as_char_array)),
                width_and_height.first,
                width_and_height.second);
            for (npy_intp index = 0; index < PyArray_SIZE(events); ++index) {
                auto payload = reinterpret_cast<uint8_t*>(PyArray_GETPTR1(events, index));
                write({*reinterpret_cast<uint64_t*>(payload + offsets[0]),
                       *reinterpret_cast<uint16_t*>(payload + offsets[1]),
                       *reinterpret_cast<uint16_t*>(payload + offsets[2]),
                       *reinterpret_cast<bool*>(payload + offsets[3]),
                       *reinterpret_cast<bool*>(payload + offsets[4])});
            }
        } else if (type_as_string == "color") {
            const auto width_and_height = get_width_and_height(stream);
            const auto events = get_events<sepia::type::color>(stream);
            const auto offsets = get_offsets<sepia::type::color>();
            sepia::write<sepia::type::color> write(
                sepia::filename_to_ofstream(std::string(filename_as_char_array)),
                width_and_height.first,
                width_and_height.second);
            for (npy_intp index = 0; index < PyArray_SIZE(events); ++index) {
                auto payload = reinterpret_cast<uint8_t*>(PyArray_GETPTR1(events, index));
                write({*reinterpret_cast<uint64_t*>(payload + offsets[0]),
                       *reinterpret_cast<uint16_t*>(payload + offsets[1]),
                       *reinterpret_cast<uint16_t*>(payload + offsets[2]),
                       *reinterpret_cast<uint8_t*>(payload + offsets[3]),
                       *reinterpret_cast<uint8_t*>(payload + offsets[4]),
                       *reinterpret_cast<uint8_t*>(payload + offsets[5])});
            }
        } else {
            throw std::runtime_error("'type' must be one of {'generic', 'dvs', 'atis', 'color'}");
        }
    } catch (const std::runtime_error& exception) {
        PyErr_SetString(PyExc_RuntimeError, exception.what());
        PyObject* result = nullptr;
        return result;
    }
    Py_RETURN_NONE;
}

/// read_dat_td loads td events from a .dat file.
static PyObject* read_dat_td(PyObject* self, PyObject* args) {
    const char* filename_as_char_array;
    if (!PyArg_ParseTuple(args, "s", &filename_as_char_array)) {
        return nullptr;
    }
    auto result = PyDict_New();
    try {
        npy_intp size = 0;
        {
            auto stream = sepia::filename_to_ifstream(filename_as_char_array);
            const auto header = dat::read_header(*stream);
            dat::td_observable(*stream, header, [&](sepia::dvs_event dvs_event) {
                ++size;
            });
        }
        auto events = stream_to_array<sepia::type::dvs>(size);
        const auto offsets = get_offsets<sepia::type::dvs>();
        npy_intp index = 0;
        auto stream = sepia::filename_to_ifstream(filename_as_char_array);
        const auto header = dat::read_header(*stream);
        dat::td_observable(*stream, header, [&](sepia::dvs_event dvs_event) {
            auto payload = reinterpret_cast<uint8_t*>(PyArray_GETPTR1(events, index));
            *reinterpret_cast<uint64_t*>(payload + offsets[0]) = dvs_event.t;
            *reinterpret_cast<uint16_t*>(payload + offsets[1]) = dvs_event.x;
            *reinterpret_cast<uint16_t*>(payload + offsets[2]) = dvs_event.y;
            *reinterpret_cast<bool*>(payload + offsets[3]) = dvs_event.is_increase;
            ++index;
        });
        PyDict_SetItem(result, PyUnicode_FromString("type"), PyUnicode_FromString("dvs"));
        PyDict_SetItem(result, PyUnicode_FromString("width"), PyLong_FromUnsignedLong(header.width));
        PyDict_SetItem(result, PyUnicode_FromString("height"), PyLong_FromUnsignedLong(header.height));
        PyDict_SetItem(result, PyUnicode_FromString("events"), reinterpret_cast<PyObject*>(events));
    } catch (const std::runtime_error& exception) {
        PyErr_SetString(PyExc_RuntimeError, exception.what());
        result = nullptr;
    }
    return result;
}

/// read_dat_aps loads td events from a .dat file.
static PyObject* read_dat_aps(PyObject* self, PyObject* args) {
    const char* filename_as_char_array;
    if (!PyArg_ParseTuple(args, "s", &filename_as_char_array)) {
        return nullptr;
    }
    auto result = PyDict_New();
    try {
        npy_intp size = 0;
        {
            auto stream = sepia::filename_to_ifstream(filename_as_char_array);
            const auto header = dat::read_header(*stream);
            dat::aps_observable(*stream, header, [&](sepia::atis_event atis_event) {
                ++size;
            });
        }
        auto events = stream_to_array<sepia::type::atis>(size);
        const auto offsets = get_offsets<sepia::type::atis>();
        npy_intp index = 0;
        auto stream = sepia::filename_to_ifstream(filename_as_char_array);
        const auto header = dat::read_header(*stream);
        dat::aps_observable(*stream, header, [&](sepia::atis_event atis_event) {
            auto payload = reinterpret_cast<uint8_t*>(PyArray_GETPTR1(events, index));
            *reinterpret_cast<uint64_t*>(payload + offsets[0]) = atis_event.t;
            *reinterpret_cast<uint16_t*>(payload + offsets[1]) = atis_event.x;
            *reinterpret_cast<uint16_t*>(payload + offsets[2]) = atis_event.y;
            *reinterpret_cast<bool*>(payload + offsets[3]) = atis_event.is_threshold_crossing;
            *reinterpret_cast<bool*>(payload + offsets[4]) = atis_event.polarity;
            ++index;
        });
        PyDict_SetItem(result, PyUnicode_FromString("type"), PyUnicode_FromString("atis"));
        PyDict_SetItem(result, PyUnicode_FromString("width"), PyLong_FromUnsignedLong(header.width));
        PyDict_SetItem(result, PyUnicode_FromString("height"), PyLong_FromUnsignedLong(header.height));
        PyDict_SetItem(result, PyUnicode_FromString("events"), reinterpret_cast<PyObject*>(events));
    } catch (const std::runtime_error& exception) {
        PyErr_SetString(PyExc_RuntimeError, exception.what());
        result = nullptr;
    }
    return result;
}

/// read_dat_td_aps loads td events from two .dat files.
static PyObject* read_dat_td_aps(PyObject* self, PyObject* args) {
    const char* td_filename_as_char_array;
    const char* aps_filename_as_char_array;
    if (!PyArg_ParseTuple(args, "ss", &td_filename_as_char_array, &aps_filename_as_char_array)) {
        return nullptr;
    }
    auto result = PyDict_New();
    try {
        npy_intp size = 0;
        {
            auto stream = sepia::filename_to_ifstream(td_filename_as_char_array);
            const auto header = dat::read_header(*stream);
            dat::td_observable(*stream, header, [&](sepia::dvs_event dvs_event) {
                ++size;
            });
        }
        {
            auto stream = sepia::filename_to_ifstream(aps_filename_as_char_array);
            const auto header = dat::read_header(*stream);
            dat::aps_observable(*stream, header, [&](sepia::atis_event atis_event) {
                ++size;
            });
        }
        auto events = stream_to_array<sepia::type::atis>(size);
        const auto offsets = get_offsets<sepia::type::atis>();
        npy_intp index = 0;
        auto td_stream = sepia::filename_to_ifstream(td_filename_as_char_array);
        auto aps_stream = sepia::filename_to_ifstream(aps_filename_as_char_array);
        const auto header = dat::read_header(*td_stream);
        {
            const auto aps_header = dat::read_header(*aps_stream);
            if (header.version != aps_header.version || header.width != aps_header.width
                || header.height != aps_header.height) {
                throw std::runtime_error("the td and aps file have incompatible headers");
            }
        }
        dat::td_aps_observable(*td_stream, *aps_stream, header, [&](sepia::atis_event atis_event) {
            auto payload = reinterpret_cast<uint8_t*>(PyArray_GETPTR1(events, index));
            *reinterpret_cast<uint64_t*>(payload + offsets[0]) = atis_event.t;
            *reinterpret_cast<uint16_t*>(payload + offsets[1]) = atis_event.x;
            *reinterpret_cast<uint16_t*>(payload + offsets[2]) = atis_event.y;
            *reinterpret_cast<bool*>(payload + offsets[3]) = atis_event.is_threshold_crossing;
            *reinterpret_cast<bool*>(payload + offsets[4]) = atis_event.polarity;
            ++index;
        });
        PyDict_SetItem(result, PyUnicode_FromString("type"), PyUnicode_FromString("atis"));
        PyDict_SetItem(result, PyUnicode_FromString("width"), PyLong_FromUnsignedLong(header.width));
        PyDict_SetItem(result, PyUnicode_FromString("height"), PyLong_FromUnsignedLong(header.height));
        PyDict_SetItem(result, PyUnicode_FromString("events"), reinterpret_cast<PyObject*>(events));
    } catch (const std::runtime_error& exception) {
        PyErr_SetString(PyExc_RuntimeError, exception.what());
        result = nullptr;
    }
    return result;
}

static PyMethodDef loris_extension_methods[] = {
    {"read_event_stream", (PyCFunction)read_event_stream, METH_VARARGS, "read events from an Event Stream file"},
    {"write_event_stream", (PyCFunction)write_event_stream, METH_VARARGS, "write events to an Event Stream file"},
    {"read_dat_td", (PyCFunction)read_dat_td, METH_VARARGS, "read events from a td .dat file"},
    {"read_dat_aps", (PyCFunction)read_dat_aps, METH_VARARGS, "read events from an aps .dat file"},
    {"read_dat_td_aps", (PyCFunction)read_dat_td_aps, METH_VARARGS, "read events from a td and aps .dat files"},
    {nullptr, nullptr, 0, nullptr}};

#if PY_MAJOR_VERSION >= 3
#define PyMODINIT_FUNC_RETURN return module
static struct PyModuleDef loris_extension_definition = {PyModuleDef_HEAD_INIT,
                                                    "loris_extension",
                                                    "loris_extension reads and writes Event Stream, and reads .dat files",
                                                    -1,
                                                    loris_extension_methods};
PyMODINIT_FUNC PyInit_loris_extension() {
    auto module = PyModule_Create(&loris_extension_definition);
#else
#define PyMODINIT_FUNC_RETURN return
PyMODINIT_FUNC initloris_extension() {
    Py_InitModule("loris_extension", loris_extension_methods);
#endif
    import_array();
    PyMODINIT_FUNC_RETURN;
}
