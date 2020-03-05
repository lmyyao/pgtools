from ctypes import *

PageSize = 8192

class PageHeaderData(Structure):
    _fields_ = [
        ('xlogid', c_uint32),
        ('xrecoff', c_uint32),
        ('pd_checksum', c_uint16),
        ('pd_flags', c_uint16),
        ('pd_lower', c_uint16),
        ('pd_upper', c_uint16),
        ('pd_special', c_uint16),
        ('pd_pagesize_version', c_uint16),
        ('pd_prune_xid', c_uint32),
    ]
    def tojson(self):
        return dict((field, getattr(self, field)) for field, _ in self._fields_)

class ItemIdData(Structure):
    _fields_ = [
        ('lp_off', c_uint32, 15),
        ('lp_flags', c_uint32, 2),
        ('lp_len', c_uint32, 15)
    ]
    
    def tojson(self):
        return {"lp_off": self.lp_off, "lp_flags": self.lp_flags, "lp_len": self.lp_len}

class HeapTupleHead(Structure):
    _fields_ = [

    ]

class PageInspect(object):
    def __init__(self, filepath, page=0):
        self._f = open(filepath, "rb")
        self.pn = page
        self.itemoffset = sizeof(PageHeaderData)

    def pgheader(self):
        self.seek(0,0)
        buffer = self.read(sizeof(PageHeaderData))
        return PageHeaderData.from_buffer_copy(buffer)

    def itemids(self):
        header = self.pgheader()
        size = header.pd_lower - self.itemoffset
        newT = ItemIdData * (size/sizeof(ItemIdData))
        self.seek(self.itemoffset, 0)
        buffer = self.read(size)
        return newT.from_buffer_copy(buffer)

    def read(self, n):
        return self._f.read(n)

    def seek(self, offset, whence):
        return self._f.seek(offset, whence)

    def close(self):
        return self._f.close()


class XLOGHeader(Structure):
    _fields_ = [
        ("xlp_magic", c_uint16),
        ("xlp_info", c_uint16),
        ("xlp_tli", c_uint32),
        ("xlp_pageaddr", c_uint64),
        ("xlp_rem_len", c_uint32)
    ]

class XLOGLongHeader(Structure):
    _fields_ = [
        ("std", XLOGHeader),
        ("xlp_sysid", c_uint64),
        ("xlp_seg_size", c_uint32),
        ("xlp_xlog_blcksz", c_uint32)
    ]

class XLOGInspect(object):
    def __init__(self, filename, page=0):
        self._f = open(filename, "rb")
        self.pn = page
        self.xLHsize = sizeof(XLOGLongHeader)
        self.xHsize = sizeof(XLOGHeader)

    def xlogheader(self):
        self.seek(0,0)
        buffer = self.read(self.xHsize)
        return XLOGHeader.from_buffer_copy(buffer)

    def xloglongheader(self):
        self.seek(0,0)
        buffer = self.read(self.xLHsize)
        return XLOGLongHeader.from_buffer_copy(buffer)

    def read(self, n):
        return self._f.read(n)

    def seek(self, offset, whence):
        return self._f.seek(offset, whence)

    def close(self):
        return self._f.close()
