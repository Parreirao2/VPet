"""Pet Components Module

This module contains the core components for the virtual pet system, including:
- Pet state management
- Stats tracking and modification
- Growth and evolution systems
- Behavior patterns
"""

import random
from datetime import datetime, timedelta
import json
import os

class PetStats:
    """Manages the pet's statistics and attributes"""
    
    def __init__(self, growth=None):
        self.growth = growth
        # Initialize with default values
        self.stats = {
            'hunger': 100,      # 0-100, 0 is starving
            'happiness': 100,   # 0-100, 0 is depressed
            'energy': 100,      # 0-100, 0 is exhausted
            'health': 100,      # 0-100, 0 is very sick
            'cleanliness': 100, # 0-100, 0 is filthy
            'social': 100,      # 0-100, 0 is lonely
            'age': 0,           # Age in days
        }
        
        # Add direct attribute access for common stats to fix errors
        self.hunger = self.stats['hunger']
        self.happiness = self.stats['happiness']
        self.energy = self.stats['energy']
        self.health = self.stats['health']
        self.cleanliness = self.stats['cleanliness']
        self.social = self.stats['social']
        self.age = self.stats['age']
        
        # Last update timestamp - moved up to ensure it's initialized early
        self.last_update = datetime.now()
        
        # Track last health reduction time for sickness
        self.last_health_reduction_time = datetime.now()
        
        # Stat decay rates (points per minute) - reduced by 4x as requested
        self.decay_rates = {
            'hunger': 0.25,      # Reduced from 1.0
            'happiness': 0.2,   # Reduced from 0.8
            'energy': 0.125,    # Reduced from 0.5
            'cleanliness': 0.175, # Reduced from 0.7
            'social': 0.15      # Reduced from 0.6
        }
        self.decay_rates = self._get_stage_adjusted_rates()
        
        # Thresholds for status effects
        self.thresholds = {
            'hunger_critical': 20,
            'energy_sleep': 0,
            'health_sick': 30,
            'happiness_sad': 30
        }
        
        # Alert thresholds for notifications
        self.alert_thresholds = {
            'low': 50,
            'critical': 30,
            'emergency': 10
        }
        
        # Track which alerts have been shown to avoid repetition
        self.shown_alerts = {}
        
        # Sickness indicator status
        self.is_sick = False
    
    # Make the class subscriptable
    def __getitem__(self, key):
        return self.stats[key]
        
    def __setitem__(self, key, value):
        self.stats[key] = value
        
        # Stat decay rates (points per minute) - reduced by 4x as requested
        self.decay_rates = {
            'hunger': 0.25,      # Reduced from 1.0
            'happiness': 0.2,   # Reduced from 0.8
            'energy': 0.125,    # Reduced from 0.5
            'cleanliness': 0.175, # Reduced from 0.7
            'social': 0.15      # Reduced from 0.6
        }
        self.decay_rates = self._get_stage_adjusted_rates()
        
        # Thresholds for status effects
        self.thresholds = {
            'hunger_critical': 20,
            'energy_sleep': 0,
            'health_sick': 30,
            'happiness_sad': 30
        }
        
        # Alert thresholds for notifications
        self.alert_thresholds = {
            'low': 50,
            'critical': 30,
            'emergency': 10
        }
        
        # Track which alerts have been shown to avoid repetition
        self.shown_alerts = {}
        
        # Last update timestamp
        self.last_update = datetime.now()
        
        # Sickness indicator status
        self.is_sick = False
    
    def update(self):
        """Update all stats based on elapsed time"""
        now = datetime.now()
        elapsed_minutes = (now - self.last_update).total_seconds() / 60.0
        self.last_update = now
        
        # Energy restoration during sleep
        if hasattr(self.growth, 'behavior') and self.growth.behavior.current_activity == 'sleeping':
            energy_gain = (elapsed_minutes * 12)  # 1% every 5 seconds (12% per minute)
            self.modify_stat('energy', energy_gain)
            
        # Update each stat based on decay rate and elapsed time
        for stat, decay_rate in self.decay_rates.items():
            self.modify_stat(stat, -decay_rate * elapsed_minutes)
        
        # Age increases over time
        if self.stats['energy'] <= 0:
            self.stats['energy'] = 0
            # Auto-sleep until 25% energy
            self.stats['energy'] += (elapsed_minutes * 60 / 5)  # Add 1% per 5 seconds
            if self.stats['energy'] > 25:
                self.stats['energy'] = 25
        else:
            self.stats['age'] += elapsed_minutes / (24 * 60)  # Convert to days
        
        # Check for stat alerts
        self.check_stat_alerts()
        
        # Update sickness status
        self.update_sickness_status()
        
        # Reduce health when sick (1% every 45 seconds)
        if self.is_sick:
            # Calculate time since last health reduction
            time_since_last_reduction = (now - self.last_health_reduction_time).total_seconds()
            
            # Check if any stat has reached 0 (excluding age)
            zero_stats = [stat for stat, value in self.stats.items() 
                         if stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social'] 
                         and value <= 0]
            
            # Double health depletion rate if any stat is at 0
            health_reduction_interval = 22.5 if zero_stats else 45  # Half the time (double the rate) if any stat is 0
            
            # Check if enough time has passed for health reduction
            if time_since_last_reduction >= health_reduction_interval:
                # Reduce health by 1%
                self.modify_stat('health', -1)
                
                # Update last health reduction time
                self.last_health_reduction_time = now
    
    def modify_stat(self, stat, amount):
        """Safely modify a stat within bounds"""
        if stat in self.stats:
            self.stats[stat] = max(0, min(100, self.stats[stat] + amount))
            
            # Update direct attribute if it exists
            if hasattr(self, stat):
                setattr(self, stat, self.stats[stat])
                
            return True
        return False
    
    def get_stat(self, stat):
        """Get the current value of a stat"""
        return self.stats.get(stat, 0)
    
    def get_status_effects(self):
        """Return a list of current status effects based on stats"""
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
        """Check if any stats have dropped below alert thresholds and trigger alerts"""
        # Define custom alert messages for each stat
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
        
        # Check each stat against thresholds
        for stat, messages in alert_messages.items():
            if stat in self.stats:
                value = self.stats[stat]
                
                # Check emergency threshold (most severe)
                if value <= self.alert_thresholds['emergency']:
                    self.trigger_alert(stat, 'emergency', messages['emergency'])
                # Check critical threshold
                elif value <= self.alert_thresholds['critical']:
                    self.trigger_alert(stat, 'critical', messages['critical'])
                # Check low threshold
                elif value <= self.alert_thresholds['low']:
                    self.trigger_alert(stat, 'low', messages['low'])
                else:
                    # Reset alert status when stat recovers
                    if stat in self.shown_alerts:
                        del self.shown_alerts[stat]
    
    def trigger_alert(self, stat, level, message):
        """Trigger an alert for a stat if it hasn't been shown recently"""
        # Only show each level of alert once until stat recovers
        if stat not in self.shown_alerts or self.shown_alerts[stat] != level:
            self.shown_alerts[stat] = level
            
            # If we have a speech bubble system, use it to show the message
            if hasattr(self, 'speech_bubble') and self.speech_bubble:
                self.speech_bubble.show_bubble('custom', message)
            
            # Alert message will be shown in speech bubble
            
    def update_sickness_status(self):
        """Update the sickness status based on health and other stats"""
        # Check if any stat is critically low (5% or less)
        critical_stats = [stat for stat, value in self.stats.items() 
                         if stat in ['hunger', 'happiness', 'energy', 'health', 'cleanliness', 'social'] 
                         and value <= 5]
        
        # Check if health is below sick threshold
        health_sick = self.stats['health'] <= self.thresholds['health_sick']
        
        # Update sickness status
        was_sick = self.is_sick
        self.is_sick = health_sick or len(critical_stats) > 0
        
        # If sickness status changed, notify the pet animation system
        if was_sick != self.is_sick and hasattr(self, 'on_sickness_changed'):
            self.on_sickness_changed(self.is_sick)
            
    def _get_stage_adjusted_rates(self):
        """Get decay rates adjusted for current growth stage"""
        if not hasattr(self, 'growth') or not self.growth:
            return self.decay_rates.copy()
            
        # Adjust rates based on growth stage
        stage = self.growth.stage if hasattr(self.growth, 'stage') else 'Baby'
        adjusted_rates = self.decay_rates.copy()
        
        # Babies have faster metabolism (decay faster)
        if stage == 'Baby':
            for stat in adjusted_rates:
                adjusted_rates[stat] *= 1.2
        # Adults have slower metabolism (decay slower)
        elif stage == 'Adult':
            for stat in adjusted_rates:
                adjusted_rates[stat] *= 0.8
                
        return adjusted_rates

class PetGrowth:
    """Manages pet growth, evolution, and life stages"""
    
    def __init__(self, stats):
        self.stats = stats
        self.stage = 'Baby'  # Baby, Child, Teen, Adult
        self.evolution_thresholds = {
            'Baby': 1,    # Age in days to evolve from Baby to Child (24 hours)
            'Child': 2,   # Age in days to evolve from Child to Teen (48 hours total)
            'Teen': 3     # Age in days to evolve from Teen to Adult (72 hours total)
        }
        self.skills = {
            'intelligence': 1,
            'strength': 1,
            'agility': 1,
            'charisma': 1
        }
        self.last_evolution_check = datetime.now()
    
    def check_evolution(self):
        """Check if pet should evolve to next stage"""
        age = self.stats.get_stat('age')
        
        if self.stage == 'Baby' and age >= self.evolution_thresholds['Baby']:
            return self.evolve_to('Child')
        elif self.stage == 'Child' and age >= self.evolution_thresholds['Child']:
            return self.evolve_to('Teen')
        elif self.stage == 'Teen' and age >= self.evolution_thresholds['Teen']:
            return self.evolve_to('Adult')
        
        return False
    
    def evolve_to(self, new_stage):
        """Handle evolution to a new stage"""
        if new_stage in ['Baby', 'Child', 'Teen', 'Adult']:
            old_stage = self.stage
            self.stage = new_stage
            # Boost stats during evolution
            for stat in ['health', 'energy']:
                self.stats.modify_stat(stat, 20)
            
            # Notify any listeners that the stage has changed
            if hasattr(self, 'on_stage_changed'):
                self.on_stage_changed(old_stage, new_stage)
                
            return True
        return False
    
    def improve_skill(self, skill, amount=0.1):
        """Improve a specific skill"""
        if skill in self.skills:
            self.skills[skill] = min(10, self.skills[skill] + amount)
            return True
        return False
    
    def get_stage(self):
        """Get current life stage"""
        return self.stage
    
    def get_skill_level(self, skill):
        """Get level of a specific skill"""
        return self.skills.get(skill, 0)

class PetBehavior:
    """Manages pet behaviors, moods, and actions"""
    
    def __init__(self, stats, growth):
        self.stats = stats
        self.growth = growth
        self.current_mood = 'normal'  # normal, happy, sad, angry, sick
        self.current_activity = 'idle'  # idle, walking, eating, playing, sleeping
        self.last_mood_update = datetime.now()
        self.last_random_action = datetime.now()
        
        # Mapping of stats to moods
        self.mood_mappings = {
            'happiness': {'low': 'sad', 'high': 'happy'},
            'energy': {'low': 'tired', 'high': 'energetic'},
            'health': {'low': 'sick', 'high': 'healthy'},
            'hunger': {'low': 'hungry', 'high': 'satisfied'}
        }
    
    def update_mood(self):
        """Update pet's mood based on current stats"""
        # Get status effects
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
        """Decide what activity the pet should do based on needs"""
        # Automatic sleep trigger
        if self.stats.get_stat('energy') <= 0:
            self.current_activity = 'sleeping'
            return self.current_activity

        # Check if enough time has passed for a random action
        now = datetime.now()
        if (now - self.last_random_action).total_seconds() < 30:
            return self.current_activity
            
        # Get current stats
        hunger = self.stats.get_stat('hunger')
        energy = self.stats.get_stat('energy')
        
        # Priority-based decision making
        if energy < 20:
            self.current_activity = 'sleeping'
        elif hunger < 30:
            self.current_activity = 'hungry'  # Looking for food
        else:
            # Random activity based on current stage and time
            activities = ['idle', 'walking']
            
            # More advanced pets have more activities
            if self.growth.get_stage() in ['Teen', 'Adult']:
                activities.extend(['playing', 'exploring'])
            
            # Choose random activity with weights
            weights = [0.5, 0.3, 0.1, 0.1][:len(activities)]
            self.current_activity = random.choices(activities, weights=weights, k=1)[0]
            self.last_random_action = now
        
        return self.current_activity
    
    def handle_interaction(self, interaction_type):
        """Handle user interaction with pet"""
        result = {
            'success': True,
            'message': '',
            'stat_changes': {}
        }
        
        if interaction_type == 'pet':
            # Petting the pet increases happiness
            self.stats.modify_stat('happiness', 5)
            self.stats.modify_stat('social', 3)
            result['message'] = 'Pet enjoyed being petted!'
            result['stat_changes'] = {'happiness': 5, 'social': 3}
            
        elif interaction_type == 'feed':
            # Feeding increases hunger but may affect other stats
            hunger_before = self.stats.get_stat('hunger')
            if hunger_before > 90:
                self.stats.modify_stat('health', -5)  # Overfeeding is unhealthy
                result['message'] = 'Pet is already full! Overfeeding is unhealthy.'
                result['stat_changes'] = {'health': -5}
            else:
                self.stats.modify_stat('hunger', 15)
                self.stats.modify_stat('happiness', 2)
                result['message'] = 'Pet enjoyed the food!'
                result['stat_changes'] = {'hunger': 15, 'happiness': 2}
            
        elif interaction_type == 'play':
            # Playing increases happiness but decreases energy
            self.stats.modify_stat('happiness', 10)
            self.stats.modify_stat('energy', -10)
            self.stats.modify_stat('social', 5)
            self.stats.modify_stat('hunger', -5)  # Playing makes pet hungry
            result['message'] = 'Pet had fun playing!'
            result['stat_changes'] = {'happiness': 10, 'energy': -10, 'social': 5, 'hunger': -5}
            
        elif interaction_type == 'clean':
            # Cleaning increases cleanliness
            self.stats.modify_stat('cleanliness', 20)
            result['message'] = 'Pet is now clean!'
            result['stat_changes'] = {'cleanliness': 20}
            
        elif interaction_type == 'medicine':
            # Medicine helps when sick
            if 'sick' in self.stats.get_status_effects():
                self.stats.modify_stat('health', 15)
                result['message'] = 'Pet is feeling better!'
                result['stat_changes'] = {'health': 15}
            else:
                self.stats.modify_stat('happiness', -5)  # Unnecessary medicine makes pet unhappy
                result['message'] = 'Pet doesn\'t need medicine right now.'
                result['stat_changes'] = {'happiness': -5}
                
        elif interaction_type == 'sleep':
            # Force pet to sleep
            self.current_activity = 'sleeping'
            result['message'] = 'Pet is now sleeping.'
            
        else:
            result['success'] = False
            result['message'] = 'Unknown interaction type.'
            
        return result
    
    def get_animation_state(self):
        """Get the current animation state based on mood and activity"""
        if self.current_activity == 'sleeping':
            return 'sleeping'
        elif self.current_activity == 'eating':
            return 'eating'
        elif self.current_activity == 'playing':
            return 'playing'
        elif self.current_activity == 'walking':
            return 'Walking'
        
        # Default animations based on mood
        if self.current_mood == 'happy':
            return 'happy'
        elif self.current_mood == 'sad':
            return 'sad'
        elif self.current_mood == 'angry':
            return 'angry'
        elif self.current_mood == 'sick':
            return 'sick'
        
        # Default
        return 'Standing'

class PetManager:
    """Main manager class that coordinates all pet components"""
    
    def __init__(self, name="Pet"):
        self._name = name  # Use private variable for name
        self.stats = PetStats()
        self.growth = PetGrowth(self.stats)
        self.stats.growth = self.growth
        self.behavior = PetBehavior(self.stats, self.growth)
        self.creation_date = datetime.now()
        self.last_save = None
        self.save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')

    @property
    def name(self):
        """Get the pet's name"""
        return self._name

    @name.setter
    def name(self, new_name):
        """Set the pet's name and update autosave filename"""
        self._name = new_name
        # Update autosave filename if it exists
        if hasattr(self, '_autosave_filepath'):
            filename = f"autosave_{new_name.replace(' ', '_')}.json"
            self._autosave_filepath = os.path.join(self.save_path, filename)
        
        # Ensure save directory exists
        os.makedirs(self.save_path, exist_ok=True)
    
    def update(self):
        """Update all pet components"""
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
        """Handle user interaction"""
        return self.behavior.handle_interaction(interaction_type)
    
    def save_pet(self, is_autosave=False):
        """Save pet state to file with backup and validation"""
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
        
        # Determine filepath based on whether this is an autosave
        if is_autosave and hasattr(self, '_autosave_filepath'):
            filepath = self._autosave_filepath
        else:
            # Create filename based on pet name and timestamp for regular saves
            filename = f"{self._name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.save_path, filename)
        
        try:
            # Create backup of previous save if it exists and this is not an autosave
            if not is_autosave and self.last_save and os.path.exists(filepath):
                backup_dir = os.path.join(self.save_path, 'backups')
                os.makedirs(backup_dir, exist_ok=True)
                backup_file = os.path.join(backup_dir, f'backup_{os.path.basename(filepath)}')
                os.rename(filepath, backup_file)
            
            # Save new file
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=4)
            
            # Verify the save was successful by reading it back
            with open(filepath, 'r') as f:
                verify_data = json.load(f)
                if verify_data != save_data:
                    raise ValueError("Save verification failed")
            
            self.last_save = datetime.now()
            return True, filepath
            
        except Exception as e:
            print(f"Error saving pet: {e}")
            # Try to restore from backup if save failed and this is not an autosave
            if not is_autosave and 'backup_file' in locals() and os.path.exists(backup_file):
                try:
                    os.rename(backup_file, filepath)
                    return False, f"Save failed, restored from backup: {str(e)}"
                except:
                    return False, f"Save failed and backup restoration failed: {str(e)}"
            return False, str(e)
    
    def autosave(self):
        """Automatically save pet state with a single overwritten file"""
        # Check if it's been more than 5 minutes since last save
        if self.last_save is None or (datetime.now() - self.last_save).total_seconds() > 300:
            try:
                # Create a fixed autosave filename
                filename = f"autosave_{self._name.replace(' ', '_')}.json"
                
                # Store current filepath for save_pet to use
                self._autosave_filepath = os.path.join(self.save_path, filename)
                
                # Call save_pet with the fixed filepath
                success, message = self.save_pet(is_autosave=True)
                
                return success, message
            except Exception as e:
                print(f"Error in autosave: {e}")
                return False, "Autosave failed"
        return False, "Too soon for autosave"
    
    @classmethod
    def load_pet(cls, filepath):
        """Load pet from save file with validation"""
        try:
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            
            # Validate required fields
            required_fields = ['name', 'stats', 'stage', 'skills', 'creation_date']
            if not all(field in save_data for field in required_fields):
                raise ValueError("Save file is missing required fields")
            
            # Create new pet instance
            pet = cls(name=save_data['name'])
            # Ensure name property is set correctly
            pet._name = save_data['name']

            # Restore evolution thresholds if available
            if 'evolution_thresholds' in save_data:
                pet.growth.evolution_thresholds = save_data['evolution_thresholds']
            
            # Restore stats with validation
            for stat, value in save_data['stats'].items():
                if not isinstance(value, (int, float)) or value < 0 or value > 100:
                    if stat != 'age':  # Age can exceed 100
                        raise ValueError(f"Invalid stat value for {stat}: {value}")
            pet.stats.stats = save_data['stats']
            
            # Validate and restore growth stage
            if save_data['stage'] not in ['Baby', 'Child', 'Teen', 'Adult']:
                raise ValueError(f"Invalid growth stage: {save_data['stage']}")
            pet.growth.stage = save_data['stage']
            
            # Restore skills with validation
            for skill, level in save_data['skills'].items():
                if not isinstance(level, (int, float)) or level < 0 or level > 10:
                    raise ValueError(f"Invalid skill level for {skill}: {level}")
            pet.growth.skills = save_data['skills']
            
            # Restore dates
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
        """Get list of available save files"""
        try:
            files = [f for f in os.listdir(self.save_path) if f.endswith('.json')]
            return files
        except Exception as e:
            print(f"Error getting save files: {e}")
            return []
    
    def delete_save_file(self, filename):
        """Delete a save file"""
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
        """Get a summary of pet stats for display"""
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
        """Update pet stats over time"""
        # Handle energy restoration during sleep
        if self.current_activity == 'sleeping':
            energy_restored = delta_time * 0.2  # 1% every 5 seconds
            self.stats.set_stat('energy', 
                min(self.stats.get_stat('energy') + energy_restored, 25))
            
            # Wake up when reaching 25% energy
            if self.stats.get_stat('energy') >= 25:
                self.current_activity = 'idle'
        else:
            # Existing stat depletion logic remains here
            pass  # Placeholder for actual implementation

    def reset_pet(self):
        """Reset pet to initial state with default stats"""
        # Create new stats instance
        self.stats = PetStats()
        
        # Reset growth
        self.growth = PetGrowth(self.stats)
        self.stats.growth = self.growth
        
        # Reset behavior
        self.behavior = PetBehavior(self.stats, self.growth)
        
        # Reset to Baby stage
        self.growth.stage = 'Baby'
        
        # Reset creation date to now
        self.creation_date = datetime.now()
        
        # Reset last save
        self.last_save = None
        
        # Return success message
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