import vv_calan

def fpga(roachIP, bof_path, valon_freq):
    roach = vv_calan(roachIP, bof_path, valon_freq)
    return roach
