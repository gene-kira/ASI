import psutil

def get_active_streams(threshold_mb=1.0):
    """
    Scans all network interfaces and returns active streams
    with entropy above the threshold.
    """
    net_data = psutil.net_io_counters(pernic=True)
    active_streams = []

    for iface, stats in net_data.items():
        in_mb = stats.bytes_recv / 1e6
        out_mb = stats.bytes_sent / 1e6
        entropy = in_mb + out_mb

        if entropy > threshold_mb:
            active_streams.append({
                "iface": iface,
                "in_mb": round(in_mb, 1),
                "out_mb": round(out_mb, 1),
                "entropy": entropy
            })

    return active_streams

