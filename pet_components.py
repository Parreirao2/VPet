import random
from datetime import datetime, timedelta
import json
import os

class PetStats:
    
    def __init__(self, growth=None):
        self.growth = growth
        self.stats = {
            'hunger': 100,
            'happiness': 100,
            'energy': 100,
            'health': 100,
            'cleanliness': 100,
            'social': 100,
            'age': 0,
        }
        
        self.hunger = self.stats['hunger']
        self.happiness = self.stats['happiness']
        self.energy = self.stats['energy']
        self.health = self.stats['health']
        self.cleanliness = self.stats['cleanliness']
        self.social = self.stats['social']
        self.age = self.stats['age']
        
        self.last_update = datetime.now()
        
        self.last_health_reduction_time = datetime.now()
        
        self.decay_rates = {
            'hunger': 0.25,
            'happiness': 0.2,
            'energy': 0.125,
            'cleanliness': 0.175,
            'social': 0.15
        }
        self.decay_rates = self._get_stage_adjusted_rates()
        
        self.thresholds = {
            'hunger_critical': 20,
            'energy_sleep': 0,
            'health_sick': 30,
            'happiness_sad': 30
        }
        
        self.alert_thresholds = {
            'low': 50,
            'critical': 30,
            'emergency': 10
        }
        
        self.shown_alerts = {}
        
        self.is_sick = False
    
    def __getitem__(self, key):
        return self.stats[key]
        
    def __setitem__(self, key, value):
        self.stats[key] = value
        
        self.decay_rates = {
            'hunger': 0.25,
            'happiness': 0.2,
            'energy': 0.125,
            'cleanliness': 0.175,
            'social': 0.15
        }
        self.decay_rates = self._get_stage_adjusted_rates()
        
        self.thresholds = {
            'hunger_critical': 20,
            'energy_sleep': 0,
            'health_sick': 30,
            'happiness_sad': 30
        }
        
        self.alert_thresholds = {
            'low': 50,
            'critical': 30,
            'emergency': 10
        }
        
        self.shown_alerts = {}
        
        self.last_update = datetime.now()
        
        self.is_sick = False
    
    def update(self):
        now = datetime.now()
        elapsed_minutes = (now - self.last_update).total_seconds() / 60.0
        self.last_update = now
        
        # Check if sleeping through either behavior or direct state
        is_sleeping = (hasattr(self, 'pet_state') and getattr(self.pet_state, 'is_sleeping', False)) or \
                      (hasattr(self.growth, 'behavior') and getattr(self.growth.behavior, 'current_activity', None) == 'sleeping')
                       
        if is_sleeping:
            # Only recover energy if below 100%
            if self.stats['energy'] < 100:
                energy_gain = (elapsed_minutes * 12)
                old_energy = self.stats['energy']
                hunger_before = self.stats['hunger']
                
                # Calculate hunger decrease (0.5% hunger for each 1% energy recovered)
                # But only if hunger is above 0%
                hunger_decrease = 0
                if hunger_before > 0:
                    hunger_decrease = min(hunger_before, energy_gain * 0.5)
                
                # Apply energy gain and hunger decrease
                self.modify_stat('energy', energy_gain)
                if hunger_decrease > 0:
                    self.modify_stat('hunger', -hunger_decrease)
                
                new_energy = self.stats['energy']
                new_hunger = self.stats['hunger']
                
                # Wake up when energy reaches 100%
                if new_energy >= 100 and hasattr(self, 'pet_state'):
                    self.pet_state.is_sleeping = False
                    self.pet_state.sleep_start_time = None
                    self.pet_state.current_animation = 'Standing'
            else:
                # Energy is at 100%, wake up the pet
                if hasattr(self, 'pet_state') and getattr(self.pet_state, 'is_sleeping', False):
                    self.pet_state.is_sleeping = False
                    self.pet_state.sleep_start_time = None
                    self.pet_state.current_animation = 'Standing'
        
        for stat, decay_rate in self.decay_rates.items():
            self.modify_stat(stat, -decay_rate * elapsed_minutes)
        
        if self.stats['energy'] <= 0:
            self.stats['energy'] = 0
            self.stats['energy'] += (elapsed_minutes * 60 / 5)
            if self.stats['energy'] > 25:
                self.stats['energy'] = 25
        else:
            self.stats['age'] += elapsed_minutes / (24 * 60)
        
        self.check_stat_alerts()
        
        self.update_sickness_status()
        
        if self.is_sick:
            time_since_last_reduction = (now - self.last_health_reduction_time).total_seconds()
            
            zero_stats = [stat for stat, value in self.stats.items() 
                         if stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social'] 
                         and value <= 0]
            
            health_reduction_interval = 22.5 if zero_stats else 45
            
            if time_since_last_reduction >= health_reduction_interval:
                self.modify_stat('health', -1)
                
                self.last_health_reduction_time = now
    
    def modify_stat(self, stat, amount):
        if stat in self.stats:
            self.stats[stat] = max(0, min(100, self.stats[stat] + amount))
            
            if hasattr(self, stat):
                setattr(self, stat, self.stats[stat])
                
            return True
        return False
    
    def get_stat(self, stat):
        return self.stats.get(stat, 0)
    
    def get_status_effects(self):
        effects = []
        
        if self.stats['hunger'] <= self.thresholds['hunger_critical']:
            effects.append('hungry')
        
        if self.stats['energy'] <= self.thresholds['energy_sleep']:
            effects.append('tired')
        
        if self.stats['health'] <= self.thresholds['health_sick']:
            effects.append('sick')
        
        if self.stats['happiness'] <= self.thresholds['happiness_sad']:
            effects.append('sad')
        
        if self.stats['cleanliness'] <= 30:
            effects.append('dirty')
        
        if self.stats['social'] <= 30:
            effects.append('lonely')
            
        return effects
        
    def check_stat_alerts(self):
        alert_messages = {
            'hunger': {
                'low': "I'm getting hungry...",
                'critical': "I'm really hungry! Please feed me!",
                'emergency': "I'm starving! Need food now!"
            },
            'happiness': {
                'low': "I'm feeling a bit sad...",
                'critical': "I'm really unhappy. Can we play?",
                'emergency': "I'm so depressed! Please help me!"
            },
            'energy': {
                'low': "I'm getting tired...",
                'critical': "I need to rest soon...",
                'emergency': "I can barely keep my eyes open!"
            },
            'health': {
                'low': "I'm not feeling very well...",
                'critical': "I think I'm getting sick!",
                'emergency': "I'm very sick! I need medicine!"
            },
            'cleanliness': {
                'low': "I could use a bath...",
                'critical': "I'm quite dirty now!",
                'emergency': "I'm filthy! Please clean me!"
            },
            'social': {
                'low': "I'm feeling a bit lonely...",
                'critical': "I miss spending time with you!",
                'emergency': "I'm so lonely! Please spend time with me!"
            }
        }
        
        for stat, messages in alert_messages.items():
            if stat in self.stats:
                value = self.stats[stat]
                
                if value <= self.alert_thresholds['emergency']:
                    self.trigger_alert(stat, 'emergency', messages['emergency'])
                elif value <= self.alert_thresholds['critical']:
                    self.trigger_alert(stat, 'critical', messages['critical'])
                elif value <= self.alert_thresholds['low']:
                    self.trigger_alert(stat, 'low', messages['low'])
                else:
                    if stat in self.shown_alerts:
                        del self.shown_alerts[stat]
    
    def trigger_alert(self, stat, level, message):
        if stat not in self.shown_alerts or self.shown_alerts[stat] != level:
            self.shown_alerts[stat] = level
            
            if hasattr(self, 'speech_bubble') and self.speech_bubble:
                self.speech_bubble.show_bubble('custom', message)
            
            
    def update_sickness_status(self):
        critical_stats = [stat for stat, value in self.stats.items() 
                         if stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social'] 
                         and value <= 5]
        
        health_sick = self.stats['health'] <= self.thresholds['health_sick']
        
        was_sick = self.is_sick
        self.is_sick = health_sick or len(critical_stats) > 0
        
        if was_sick != self.is_sick and hasattr(self, 'on_sickness_changed'):
            self.on_sickness_changed(self.is_sick)
            
    def _get_stage_adjusted_rates(self):
        if not hasattr(self, 'growth') or not self.growth:
            return self.decay_rates.copy()
            
        stage = self.growth.stage if hasattr(self.growth, 'stage') else 'Baby'
        adjusted_rates = self.decay_rates.copy()
        
        if stage == 'Baby':
            for stat in adjusted_rates:
                adjusted_rates[stat] *= 1.2
        elif stage == 'Adult':
            for stat in adjusted_rates:
                adjusted_rates[stat] *= 0.8
                
        return adjusted_rates

class PetGrowth:
    
    def __init__(self, stats):
        self.stats = stats
        self.stage = 'Baby'
        self.evolution_thresholds = {
            'Baby': 30,
            'Child': 60,
            'Teen': 90
        }
        self.skills = {
            'intelligence': 1,
            'strength': 1,
            'agility': 1,
            'charisma': 1
        }
        self.last_evolution_check = datetime.now()
    
    def check_evolution(self):
        age = self.stats.get_stat('age')
        
        if self.stage == 'Baby' and age >= self.evolution_thresholds['Baby']:
            return self.evolve_to('Child')
        elif self.stage == 'Child' and age >= self.evolution_thresholds['Child']:
            return self.evolve_to('Teen')
        elif self.stage == 'Teen' and age >= self.evolution_thresholds['Teen']:
            return self.evolve_to('Adult')
        
        return False
    
    def evolve_to(self, new_stage):
        if new_stage in ['Baby', 'Child', 'Teen', 'Adult', 'Special']:
            old_stage = self.stage
            self.stage = new_stage
            
            if hasattr(self.stats, 'pet_state'):
                self.stats.pet_state.stage = new_stage
            
            for stat in ['health', 'energy']:
                self.stats.modify_stat(stat, 20)
            
            if hasattr(self, 'on_stage_changed'):
                self.on_stage_changed(old_stage, new_stage)
                
            return True
        return False
    
    def improve_skill(self, skill, amount=0.1):
        if skill in self.skills:
            self.skills[skill] = min(10, self.skills[skill] + amount)
            return True
        return False
    
    def get_stage(self):
        return self.stage
    
    def get_skill_level(self, skill):
        return self.skills.get(skill, 0)

class PetBehavior:
    
    def __init__(self, stats, growth):
        self.stats = stats
        self.growth = growth
        self.current_mood = 'normal'
        self.current_activity = 'idle'
        self.last_mood_update = datetime.now()
        self.last_random_action = datetime.now()
        
        self.mood_mappings = {
            'happiness': {'low': 'sad', 'high': 'happy'},
            'energy': {'low': 'tired', 'high': 'energetic'},
            'health': {'low': 'sick', 'high': 'healthy'},
            'hunger': {'low': 'hungry', 'high': 'satisfied'}
        }
    
    def update_mood(self):
        effects = self.stats.get_status_effects()
        
        if 'sick' in effects:
            self.current_mood = 'sick'
        elif 'hungry' in effects and 'tired' in effects:
            self.current_mood = 'angry'
        elif 'sad' in effects or 'lonely' in effects:
            self.current_mood = 'sad'
        elif self.stats.get_stat('happiness') > 80:
            self.current_mood = 'happy'
        else:
            self.current_mood = 'normal'
        
        return self.current_mood
    
    def decide_activity(self):
        now = datetime.now()
        if (now - self.last_random_action).total_seconds() < 30:
            return self.current_activity
            
        hunger = self.stats.get_stat('hunger')
        energy = self.stats.get_stat('energy')
        
        # Use the same threshold as in main.py (15%)
        if energy < 15:  # Changed from 5 to 15 to match main.py
            self.current_activity = 'sleeping'
            if not getattr(self.stats.pet_state, 'is_sleeping', False):
                self.stats.pet_state.is_sleeping = True
                self.stats.pet_state.sleep_start_time = datetime.now()
        elif hunger < 30:
            self.current_activity = 'hungry'
        else:
            activities = ['idle', 'walking']
            
            if self.growth.get_stage() in ['Teen', 'Adult']:
                activities.extend(['playing', 'exploring'])
            
            weights = [0.5, 0.3, 0.1, 0.1][:len(activities)]
            self.current_activity = random.choices(activities, weights=weights, k=1)[0]
            self.last_random_action = now
        
        return self.current_activity
    
    def handle_interaction(self, interaction_type):
        result = {
            'success': True,
            'message': '',
            'stat_changes': {}
        }
        
        if interaction_type == 'pet':
            self.stats.modify_stat('happiness', 5)
            self.stats.modify_stat('social', 3)
            result['message'] = 'Pet enjoyed being petted!'
            result['stat_changes'] = {'happiness': 5, 'social': 3}
            
        elif interaction_type == 'feed':
            hunger_before = self.stats.get_stat('hunger')
            if hunger_before > 90:
                self.stats.modify_stat('health', -5)
                result['message'] = 'Pet is already full! Overfeeding is unhealthy.'
                result['stat_changes'] = {'health': -5}
            else:
                self.stats.modify_stat('hunger', 15)
                self.stats.modify_stat('happiness', 2)
                result['message'] = 'Pet enjoyed the food!'
                result['stat_changes'] = {'hunger': 15, 'happiness': 2}
            
        elif interaction_type == 'play':
            self.stats.modify_stat('happiness', 10)
            self.stats.modify_stat('energy', -10)
            self.stats.modify_stat('social', 5)
            self.stats.modify_stat('hunger', -5)
            result['message'] = 'Pet had fun playing!'
            result['stat_changes'] = {'happiness': 10, 'energy': -10, 'social': 5, 'hunger': -5}
            
        elif interaction_type == 'clean':
            self.stats.modify_stat('cleanliness', 20)
            result['message'] = 'Pet is now clean!'
            result['stat_changes'] = {'cleanliness': 20}
            
        elif interaction_type == 'medicine':
            if 'sick' in self.stats.get_status_effects():
                self.stats.modify_stat('health', 15)
                result['message'] = 'Pet is feeling better!'
                result['stat_changes'] = {'health': 15}
            else:
                self.stats.modify_stat('happiness', -5)
                result['message'] = "Pet doesn't need medicine right now."
                result['stat_changes'] = {'happiness': -5}
                
        elif interaction_type == 'sleep':
            self.current_activity = 'sleeping'
            result['message'] = 'Pet is now sleeping.'
            
        else:
            result['success'] = False
            result['message'] = 'Unknown interaction type.'
            
        return result
    
    def get_animation_state(self):
        if self.current_activity == 'sleeping':
            return 'sleeping'
        elif self.current_activity == 'eating':
            return 'eating'
        elif self.current_activity == 'playing':
            return 'playing'
        elif self.current_activity == 'walking':
            return 'Walking'
        
        if self.current_mood == 'happy':
            return 'happy'
        elif self.current_mood == 'sad':
            return 'sad'
        elif self.current_mood == 'angry':
            return 'angry'
        elif self.current_mood == 'sick':
            return 'sick'
        
        return 'Standing'

class PetManager:
    
    def __init__(self, name="Pet"):
        self._name = name
        self.stats = PetStats()
        self.growth = PetGrowth(self.stats)
        self.stats.growth = self.growth
        self.behavior = PetBehavior(self.stats, self.growth)
        self.creation_date = datetime.now()
        self.last_save = None
        self.save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
        if hasattr(self, '_autosave_filepath'):
            filename = f"autosave_{new_name.replace(' ', '_')}.json"
            self._autosave_filepath = os.path.join(self.save_path, filename)
        
        os.makedirs(self.save_path, exist_ok=True)
    
    def update(self):
        self.stats.update()
        evolution_occurred = self.growth.check_evolution()
        self.behavior.update_mood()
        activity = self.behavior.decide_activity()
        
        return {
            'evolution': evolution_occurred,
            'mood': self.behavior.current_mood,
            'activity': activity,
            'animation': self.behavior.get_animation_state(),
            'stage': self.growth.get_stage()
        }
    
    def handle_interaction(self, interaction_type):
        return self.behavior.handle_interaction(interaction_type)
    
    def save_pet(self, is_autosave=False):
        save_data = {
            'name': self._name,
            'stats': self.stats.stats,
            'stage': self.growth.stage,
            'skills': self.growth.skills,
            'creation_date': self.creation_date.isoformat(),
            'save_date': datetime.now().isoformat(),
            'version': '1.0',
            'evolution_thresholds': self.growth.evolution_thresholds,
            'game_progress': getattr(self, 'game_progress', {'number_guesser': 1, 'reaction_test': 1, 'ball_clicker': 1})
        }
        
        if is_autosave and hasattr(self, '_autosave_filepath'):
            filepath = self._autosave_filepath
        else:
            filename = f"{self._name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.save_path, filename)
        
        try:
            if not is_autosave and self.last_save and os.path.exists(filepath):
                backup_dir = os.path.join(self.save_path, 'backups')
                os.makedirs(backup_dir, exist_ok=True)
                backup_file = os.path.join(backup_dir, f'backup_{os.path.basename(filepath)}')
                os.rename(filepath, backup_file)
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=4)
            
            with open(filepath, 'r') as f:
                verify_data = json.load(f)
                if verify_data != save_data:
                    raise ValueError("Save verification failed")
            
            self.last_save = datetime.now()
            return True, filepath
            
        except Exception as e:
            print(f"Error saving pet: {e}")
            if not is_autosave and 'backup_file' in locals() and os.path.exists(backup_file):
                try:
                    os.rename(backup_file, filepath)
                    return False, f"Save failed, restored from backup: {str(e)}"
                except:
                    return False, f"Save failed and backup restoration failed: {str(e)}"
            return False, str(e)
    
    def autosave(self):
        if self.last_save is None or (datetime.now() - self.last_save).total_seconds() > 300:
            try:
                filename = f"autosave_{self._name.replace(' ', '_')}.json"
                
                self._autosave_filepath = os.path.join(self.save_path, filename)
                
                success, message = self.save_pet(is_autosave=True)
                
                return success, message
            except Exception as e:
                print(f"Error in autosave: {e}")
                return False, "Autosave failed"
        return False, "Too soon for autosave"
    
    @classmethod
    def load_pet(cls, filepath):
        try:
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            required_fields = ['name', 'stats', 'stage', 'skills', 'creation_date']
            if not all(field in save_data for field in required_fields):
                raise ValueError("Save file is missing required fields")
            
            pet = cls(name=save_data['name'])
            pet._name = save_data['name']

            if 'evolution_thresholds' in save_data:
                pet.growth.evolution_thresholds = save_data['evolution_thresholds']
            
            for stat, value in save_data['stats'].items():
                if not isinstance(value, (int, float)) or value < 0 or value > 100:
                    if stat != 'age':
                        raise ValueError(f"Invalid stat value for {stat}: {value}")
            pet.stats.stats = save_data['stats']
            
            if save_data['stage'] not in ['Baby', 'Child', 'Teen', 'Adult']:
                raise ValueError(f"Invalid growth stage: {save_data['stage']}")
            pet.growth.stage = save_data['stage']
            
            for skill, level in save_data['skills'].items():
                if not isinstance(level, (int, float)) or level < 0 or level > 10:
                    raise ValueError(f"Invalid skill level for {skill}: {level}")
            pet.growth.skills = save_data['skills']
            
            pet.creation_date = datetime.fromisoformat(save_data['creation_date'])
            
            return pet, None
            
        except json.JSONDecodeError:
            return None, "Invalid save file format"
        except ValueError as e:
            return None, str(e)
        except Exception as e:
            print(f"Error loading pet: {e}")
            return None, str(e)
    
    def get_save_files(self):
        try:
            files = [f for f in os.listdir(self.save_path) if f.endswith('.json')]
            return files
        except Exception as e:
            print(f"Error getting save files: {e}")
            return []
    
    def delete_save_file(self, filename):
        try:
            filepath = os.path.join(self.save_path, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True, f"Successfully deleted {filename}"
            else:
                return False, "File not found"
        except Exception as e:
            print(f"Error deleting save file: {e}")
            return False, str(e)
    
    def get_stats_summary(self):
        return {
            'name': self._name,
            'stage': self.growth.get_stage(),
            'age': round(self.stats.get_stat('age'), 1),
            'hunger': self.stats.get_stat('hunger'),
            'happiness': self.stats.get_stat('happiness'),
            'energy': self.stats.get_stat('energy'),
            'health': self.stats.get_stat('health'),
            'cleanliness': self.stats.get_stat('cleanliness'),
            'social': self.stats.get_stat('social'),

            'status_effects': self.stats.get_status_effects()
        }

    def update_stats(self, delta_time):
        if self.current_activity == 'sleeping':
            energy_restored = delta_time * 0.2
            self.stats.set_stat('energy', 
                min(self.stats.get_stat('energy') + energy_restored, 25))
            
            if self.stats.get_stat('energy') >= 25:
                self.current_activity = 'idle'
        else:
            pass

    def reset_pet(self):
        self.stats = PetStats()
        
        self.growth = PetGrowth(self.stats)
        self.stats.growth = self.growth
        
        self.behavior = PetBehavior(self.stats, self.growth)
        
        self.growth.stage = 'Baby'
        
        self.creation_date = datetime.now()
        
        self.last_save = None
        
        return True, "Pet has been reset to initial state."

if __name__ == "__main__":
    pet = PetManager()
    print("Virtual Pet System Started!")
    try:
        while True:
            try:
                pet.update()
            except Exception as e:
                print(f"Error during update: {e}")
                raise
    except KeyboardInterrupt:
        print("\nSaving pet state...")
        pet.save_pet()
        print("Goodbye!")