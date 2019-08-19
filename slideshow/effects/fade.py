def get(fade_duration):
    return "blend=all_expr='A*(1-T/%s)+B*(T/%s)':shortest=1" %(fade_duration, fade_duration)