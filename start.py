import config_reader

# Read the config
config = config_reader.get_config()
    
# Start Flask
import application
application.start_webapp(config)
