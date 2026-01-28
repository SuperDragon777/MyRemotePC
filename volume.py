from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER

def volume(percent):
    """Set system volume to a specific percentage (0-100)."""
    if not 0 <= percent <= 100:
        raise ValueError("Volume must be between 0 and 100.")
    
    speakers = AudioUtilities.GetSpeakers()
    interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    vol = cast(interface, POINTER(IAudioEndpointVolume))
    
    #current = vol.GetMasterVolumeLevelScalar()
    vol.SetMasterVolumeLevelScalar(percent / 100.0, None)
    #new = vol.GetMasterVolumeLevelScalar()
    
    #print(f"Volume: {current * 100:.0f}% → {new * 100:.0f}%")

def current_volume():
    """Get the current system volume as a percentage (0-100)."""
    speakers = AudioUtilities.GetSpeakers()
    interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    vol = cast(interface, POINTER(IAudioEndpointVolume))
    
    current = vol.GetMasterVolumeLevelScalar()
    return int(current * 100)
