from collections import namedtuple


# Most routers seem to use a single IP ID counter shared across
# all interfaces and protocols, but any IP ID-based alias resolution
# technique must account for those that do not. Some routers set
# the IP ID to zero or some other constant value, a random value,
# or the value used in the probe packet.
IpIDModeTemplate = namedtuple(typename='IpIDMode',
                      field_names=['Normal',
                                   'Const',
                                   'ProbVal',
                                   'Unknown'])
IpIDMode = IpIDModeTemplate(Unknown='Unknown',
                            Normal='Normal',
                            Const='Constant',
                            ProbVal='Probe Packet Value')

# 默认目的端口号
DefaultDPort = 33433