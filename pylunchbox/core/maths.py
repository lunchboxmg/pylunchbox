import numpy as np
from numpy import ndarray, identity, zeros, cross, concatenate, empty
from numpy import sqrt as npsqrt, sum as npsum, dot
from math import sin, cos, tan

__author__ = "lunchboxmg"

from ecs import Component
from constants import *

# Type Conversions

FLOAT32 = np.float32
UINT32 = np.uint32
FLOAT64 = np.float64

def make_float_array(list_):
    """ Convert the input list into a numpy array of floats. """

    return np.array(list_, dtype=FLOAT32)

# Vector functions

def get_length(vector):
    """ Retrieve the length of the input vector. """

    return npsqrt(npsum(vector*vector))

def normalize(vector):
    """ Normalize the input vector. """

    norm = npsqrt(npsum(vector*vector))
    return vector / norm

def proj(u, n):
    """ Projection of vector `u` onto the plane whose normal is `n`. """

    top = dot(u, n)
    bot = npsum(n * n)
    return u - (top/bot) * n

def average(vectors):
    """ Take the average of the input list of vectors. """

    summation = Vector3f(0, 0, 0)
    for v in vectors:
        summation += v
    if get_length(summation) == 0:
        print vectors
    return summation / get_length(summation)

# Vector classes

class Vector2f(ndarray):
    """
    The Vector2f class is a subclassed numpy array composed of 2 floats.

    Gives a view of the numpy array made from x, y (or z) that allows the
    user to access elements by their component name.
    """

    _UNIT = FLOAT32

    def __new__(cls, x, y):
        """ Create a numpy array of elements x and y.

        Parameters
        ----------
        x : :obj:`float`
        
        y : :obj:`float`
        """

        obj = np.asarray((x, y), cls._UNIT).view(cls)
        return obj

    def __array_finalize__(self, obj): pass

    def get_x(self): return self[0]
    def set_x(self, value): self[0] = self._UNIT(value)
    x = property(get_x, set_x, doc="X-Component of the Vector.")

    def get_y(self): return self[1]
    def set_y(self, value): self[1] = self._UNIT(value)
    y = property(get_y, set_y, doc="Y-Component of the Vector.")

    def get_length(self):
        """Retrieve the length of this vector. """

        return get_length(self)

    def normalize(self, out=None):
        """ Normalize this vector inplace.

        Parameters
        ----------
        out : :class:`ndarray`, optional
            the ndarray or vector that the result will be placed in.
        """

        new_array = normalize(self)
        if out:
            out[:] = new_array[:]
        else:
            self[:] = new_array[:]

class Vector2i(Vector2f):

    _UNIT = UINT32

class Vector2d(Vector2f):

    _UNIT = FLOAT64

class Vector3f(Vector2f):
    """
    The Vector3f class is a subclassed numpy array composed of 3 floats.

    Gives a view of the numpy array made from x, y, z that allows the
    user to access elements by their component name.
    """

    _UNIT = FLOAT32

    def __new__(cls, x, y, z=0):
        """ Create numpy array of elements x, y, z.

        Parameters:
        ===========
        x (:obj:`float`): x-component.
        y (:obj:`float`): y-component.
        z (:obj:`float`): z-component.
        """

        obj = np.asarray((x, y, z), cls._UNIT).view(cls)
        return obj

    def __array_finalize__(self, obj): pass

    def get_z(self): return self[2]
    def set_z(self, value): self[2] = self._UNIT(value)
    z = property(get_z, set_z, doc="Z-Component of the Vector.")

    def get_xy(self):
        """ Retrieve a Vector2f of the x, y components. """

        return Vector2f(self.x, self.y)

    def get_xz(self):
        """ Retrieve a Vector2f of the x, z components. """

        return Vector2f(self.x, self.z)

    def get_yz(self):
        """ Retrieve a Vector2f of the y, z components. """

        return Vector2f(self.y, self.z)

    def transform(self, matrix):
        """ Transform this vector by a matrix. """


        if matrix.shape[1] == 4:
            v = np.array([self[0], self[1], self[2], 1.0])
        elif matrix.shape[1] == 3:
            v = self

        try:
            return Vector3f(*matrix.dot(v)[:3])
        except ValueError as e:
            print e
            return None

    def as_vector4f(self):
        """ Create an :class:`Vector4f` version of this vector. """
        
        
class Vector3i(Vector3f):

    _UNIT = UINT32

# Matrix operations

class Vector4f(Vector3f):

    def __new__(cls, x, y, z, w=1.0):
        """ Create numpy array of elements x, y, z.

        Parameters:
        ===========
        x (:obj:`float`): x-component.
        y (:obj:`float`): y-component.
        z (:obj:`float`): z-component.
        w (:obj:`float`): w-component.
        """

        obj = np.asarray((x, y, z, w), cls._UNIT).view(cls)
        return obj

    def get_w(self): return self[2]
    def set_w(self, value): self[2] = self._UNIT(value)
    w = property(get_w, set_w, doc="Z-Component of the Vector.")

    def get_xyz(self):
        """ Retrieve a 3D vector from the x, y, z components of this vector. """

        return Vector3f(self._x, self._y, self._z)

X_AXIS = Vector3f(1, 0, 0)
Y_AXIS = Vector3f(0, 1, 0)
Z_AXIS = Vector3f(0, 0, 1)

V_ZERO = Vector3f(0, 0, 0)
V_ONE = Vector3f(1, 1, 1)

class Transformation(Component):
    
    def __init__(self, position=V_ZERO, rotation=V_ZERO, scale=V_ONE):
        """ Constructor.
        
        Parameters
        ----------
        position : :class:`Vector3f`
            The position the entity needs to be translated to from the origin.
        rotation : :class:`Vector3f`, units = degrees
            The amount of rotation about each coordinate axis. 
        scale : :class:`Vector3f`
            The amount to scale the mesh along each coordinate axis.
        """
        
        self._position = position
        self._rotation = rotation
        self._scale = scale
        self._matrix = identity(4)
        self._dirty = True
        
    def update(self):
        """ Update the internal model matrix. """
        
        if self._dirty:
            r = self._rotation
            m = identity(4)
            m = translate(m, self._position)
            if r.y: m = rotate(m, r.y, Y_AXIS)
            if r.z: m = rotate(m, r.z, Z_AXIS)
            if r.x: m = rotate(m, r.x, X_AXIS)
            m = scale(m, self._scale)
            self._matrix = m
            self._dirty = False
            return m
        return None
    
    def get_matrix(self):
        """ Get the model matrix. """
        
        if self._dirty: self.update()
        return self._matrix
    
    def set_position(self, new_position):
        """ Set the position of this entity. """

        self._position = new_position
        self._dirty = True

    def get_position(self):
        """ Retrieve the current position of this entity. """
        
        return self._position
    
    def set_rotation(self, new_rotation):
        """ Set the rotation of this entity. """

        self._rotation = new_rotation
        self._dirty = True

    def get_rotation(self):
        """ Retrieve the current rotation of this entity. """
        
        return self._rotation

    def set_scale(self, new_scale):
        """ Set the position of this entity. """

        self._scale = new_scale
        self._dirty = True

    def get_scale(self):
        """ Retrieve the current position of this entity. """
        
        return self._scale

    def is_dirty(self):
        """ Determine if any of the transformation parameters has been 
        altered. """
        
        return self._dirty

def calc_surface_normal(p1, p2, p3):
    """ Calculate the surface normal of the input points that create the
    sides of a triangle. """

    u = p2 - p1
    v = p3 - p1

    nx = u.y * v.z - u.z * v.y
    ny = u.z * v.x - u.x * v.z 
    nz = u.x * v.y - u.y * v.x

    return Vector3f(nx, ny, nz)

def translate(m, v):
    """ Perform a translation on the input matrix `m` using `v` position
    vector. """

    r = np.copy(m)
    r[3] = m[0] * v[0] + m[1] * v[1] + m[2] * v[2] + m[3]

    return r

def rotate(m, angle, v):
    """ Rotate about the `v` axis by the `angle`.

    NOTE: v is in degrees. """

    c = cos(angle*D2R)
    s = sin(angle*D2R)

    axis = normalize(v)
    temp = (1.0 - c) * axis

    # Setup rotation matrix
    rot00 = c + temp[0] * axis[0]
    rot01 = temp[0] * axis[1] + s * axis[2]
    rot02 = temp[0] * axis[2] - s * axis[1]

    rot10 = temp[1] * axis[0] - s * axis[2]
    rot11 = c + temp[1] * axis[1]
    rot12 = temp[1] * axis[2] + s * axis[0]

    rot20 = temp[2] * axis[0] + s * axis[1]
    rot21 = temp[2] * axis[1] - s * axis[0]
    rot22 = c + temp[2] * axis[2]

    # Apply rotation
    r = zeros((4, 4), dtype=FLOAT32)
    r[0] = m[0] * rot00 + m[1] * rot01 + m[2] * rot02
    r[1] = m[0] * rot10 + m[1] * rot11 + m[2] * rot12
    r[2] = m[0] * rot20 + m[1] * rot21 + m[2] * rot22
    r[3] = m[3]

    return r

def scale(m, v):
    """ Apply scaling to the input matrix `m`. """

    r = zeros((4, 4), dtype=FLOAT32)
    r[0] = m[0] * v[0]
    r[1] = m[1] * v[1]
    r[2] = m[2] * v[2]
    r[3] = m[3]

    return r

def look_at_RH(eye, center, up):
    """ Camera view matrix utilizing the right hand coordinate system. """

    f = normalize(center - eye)
    s = normalize(cross(f, up))
    u = cross(s, f)

    r = identity(4, dtype=FLOAT32)
    r[0:3, 0] = s
    r[0:3, 1] = u
    r[0:3, 2] = -f
    r[3, 0] = -dot(s, eye)
    r[3, 1] = -dot(u, eye)
    r[3, 2] = dot(f, eye)

    return r

def look_at_LH(eye, center, up):
    """ Camera view matrix utilizing the left hand coordinate system. """

    f = normalize(center - eye)
    s = normalize(cross(up, f))
    u = cross(s, f)

    r = identity(4, dtype=FLOAT32)
    r[0:3, 0] = s
    r[0:3, 1] = u
    r[0:3, 2] = f
    r[3, 0] = -dot(s, eye)
    r[3, 1] = -dot(u, eye)
    r[3, 2] = -dot(f, eye)

    return r

def perspective_RH(fovy, aspect, znear, zfar):

    fovy *= D2R
    tan_half_fovy = tan(fovy * 0.5)

    r = zeros((4,4), dtype=FLOAT32)
    r[0, 0] = 1.0 / (aspect * tan_half_fovy)
    r[1, 1] = 1.0 / (tan_half_fovy)
    r[2, 3] = -1.0

    # Option 1 (if GLM_CLIP_SPACE == GL_DEPTH_ZERO_TO_ONE)
    r[2, 2] = zfar / (znear - zfar)
    r[3, 2] = -(zfar * znear) / (zfar - znear)

    # Option 2
    #r[2, 2] = -(zfar + znear) / (zfar - znear)
    #r[3, 2] = -2.0 * zfar * znear / (zfar - znear)

    return r

def perspective_LH(fovy, aspect, znear, zfar):
    """ Prespective projection for 3D rendering that utilizes the
    left hand coordinate system. """

    fovy *= D2R
    tan_half_fovy = tan(fovy * 0.5)

    r = zeros((4,4), dtype=FLOAT32)
    r[0, 0] = 1.0 / (aspect * tan_half_fovy)
    r[1, 1] = 1.0 / tan_half_fovy
    r[2, 3] = 1.0

    # Option 1 (if GLM_CLIP_SPACE == GL_DEPTH_ZERO_TO_ONE)
    r[2, 2] = zfar / (zfar - znear)
    r[3, 2] = -(zfar * znear) / (zfar - znear)

    # Option 2
    #r[2, 2] = (zfar + znear) / (zfar - znear)
    #r[3, 2] = -2.0 * zfar * znear / (zfar - znear)

    return r

def ortho_RH(left, right, bottom, top, znear, zfar):
    """ Orthographic projection for 3D rendering that utilizes the
    right hand coordinate system. """

    r = identity(4, dtype=FLOAT32)

    r[0, 0] = 2.0 / (right - left)
    r[1, 1] = 2.0 / (top - bottom)
    r[3, 0] = -(right + left) / (right - left)
    r[3, 1] = -(top + bottom) / (top - bottom)

    # Option 1 (if GLM_DEPTH_CLIP_SPACE == GLM_DEPTH_ZERO_TO_ONE)
    r[2, 2] = -1.0 / (zfar - znear)
    r[3, 2] = -znear / (zfar - znear)

    # else
    #r[2, 2] = -2.0 / (zfar - znear)
    #r[3, 2] = -(zfar + znear) / (zfar - znear)

    return r

def ortho_2D(left, right, bottom, top):
    """ Orthographic projection for 2D rendering. """

    r = identity(4, dtype=FLOAT32)
    r[0, 0] = 2.0 / (right - left)
    r[1, 1] = 2.0 / (top - bottom)
    r[2, 2] = -1.0
    r[3, 0] = -(right + left) / (right - left)
    r[3, 1] = -(top + bottom) / (top - bottom)

    return r

# Math functions

def clamp(x, x_min, x_max):
    """ Force the input value `x` to be within the bounds of [x_min, x_max]. """

    if x < x_min: return x_min
    elif x > x_max: return x_max
    return x

if __name__ == "__main__":

    test3f = Vector3f(1, 2, 3) + np.array([1, 2, 3])
    test3f.normalize()

    print type(test3f)
    print test3f.z

    test2f = Vector2f(2, 3)
    print id(test2f.base)
    test2f.normalize()
    print id(test2f.base)

    test2 = Vector3f(test2f.x, test2f.y)
    test2.normalize()
    print test2
    print id(test2.base)

    test2f += [1, 3]
    print id(test2f.base)
    print test2f

    test3 = test2.get_xy()
    print type(test3)
    print id(test3.base)

    vs = [Vector3f(i*.5, i + 2.0, i*3) for i in xrange(4)]
    for v in vs: print v
    print average(vs)

    test_pos3 = Vector3f(1.0, 1.0, 1.0)
    test_pos4 = Vector4f(1.0, 1.0, 1.0, 1.0)

    matrix = identity(4, FLOAT32)
    matrix = scale(matrix, Vector3f(1, 1, 1))
    print ">>>", test_pos3.transform(matrix)
    matrix = rotate(matrix, 45.0, Vector3f(1, 0, 0))
    print ">>>", test_pos3.transform(matrix).get_xy()

    pos1 = Vector3f(1.0, 0.0, 0.0)
    trans1 = Transformation(Vector3f(1.0, 0.0, 2.0))
    new_pos1 = pos1.transform(trans1.get_matrix().T)
    print new_pos1