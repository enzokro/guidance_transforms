# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_schedules.ipynb.

# %% auto 0
__all__ = ['get_cos_sched']

# %% ../nbs/02_schedules.ipynb 3
import math 

# %% ../nbs/02_schedules.ipynb 4
def get_cos_sched(num_steps: int = 50,
                  max_val: float = 7.5,
                  min_val: float = 0.15,
                  num_cycles: float = 0.5,
                  num_warmup_steps: int = 0,
                  warmup_init_val: float = 0.,
                  k_decay:float = 1.,
                  cycle_mul: float = 1.,
                  cycle_decay:float = 1.,
                  cycle_limit = 1.) -> list:
    '''Creates a cosine schedule based on the given parameters.
    
    Args:
        num_steps: Number of total steps in the schedules. 
        max_val: The maximum value in the schedule. 
        min_val: The minimum number in the schedule. 
        num_cycles: How many full cosine schedules to sweep. By default, 0.5.
        num_warmup_steps: Over how many steps to warmup.  
        cycle_mul: Param for timm scheduler.
        cycle_decay: Param for timm schedulers.
        cycle_limit: Param for timm schedulers.
        k_decay: Param for timm schedulers.  
        
    The cycle_* and k_decay `timm` parmeters are described in better detail here:
        https://timm.fast.ai/SGDR#CosineLRScheduler
    These args offer a lot of powerful flexibility in guiding the cosine scheduler.
        TODO: experiment with these settings for diffusion.  
        
    NOTE: cycle_* parameters might not work as intended, since we are dealing with "one" epoch.
        TODO: investigate
    
    Based on a combo of HuggingFace and timm schedulers:
        https://github.com/rwightman/pytorch-image-models/blob/main/timm/scheduler/cosine_lr.py
        https://github.com/huggingface/transformers/blob/v4.24.0/src/transformers/optimization.py#L104
    '''

    def cos_sched_helper(current_step):
        "Helper to compute cosine values."
        
        # get the warmup value
        if current_step < num_warmup_steps:
            init_offset = float(current_step * (max_val - warmup_init_val)) / float(max(1, num_warmup_steps))
            return warmup_init_val + init_offset
        
        # else get the regular scheduled values
        else:

            if cycle_mul != 1:
                i = math.floor(math.log(1 - current_step / num_steps * (1 - cycle_mul), cycle_mul))
                t_i = cycle_mul ** i * num_steps
                t_curr = current_step - (1 - cycle_mul ** i) / (1 - cycle_mul) * num_steps
            else:
                i = current_step // num_steps #
                t_i = num_steps
                t_curr = current_step - (num_steps * i)

            # find the scaled maximum value based on cycle_decay
            gamma = cycle_decay ** i
            scaled_max = max_val * gamma
            scaled_mag = 0.5 * (scaled_max - min_val)
            
            # find completion offset based on current step and k-decay
            t_curr = (t_curr - num_warmup_steps)
            t_i = max(1, num_steps - num_warmup_steps)
            scaled_progress = (t_curr ** k_decay) / (t_i ** k_decay)
            
            if i < cycle_limit:
                cos_val = (1 + math.cos(math.pi * 2 * num_cycles * scaled_progress))
                val = min_val + scaled_mag * cos_val
            else:
                val = min_val

            return val

    # get the actual schedule value
    vals = [cos_sched_helper(i) for i in range(num_steps)]
    return vals

