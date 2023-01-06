"""
This script generates a synthetic "alexa" dataset.

See the corresponding tutorial for more details:
https://siliconlabs.github.io/mltk/mltk/tutorials/synthetic_audio_dataset_generation.html

"""

# Import the necessary Python packages
import os
import json
import tqdm
import tempfile
from mltk.utils.audio_dataset_generator import (
    AudioDatasetGenerator,
    Keyword,
    Augmentation,
    VoiceRate,
    VoicePitch
)


# NOTE: The following credentials are provided as an example.
#       You must generate your own credentials to run this example

###################################################################################################
# Configure your Azure credentials
# See: https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/get-started-text-to-speech?pivots=programming-language-python
os.environ['SPEECH_KEY'] = 'e8699507e7c04a4cb8afdba62986987c'
os.environ['SPEECH_REGION'] = 'westus2'


###################################################################################################
# Configure your Google credentials
# See: https://codelabs.developers.google.com/codelabs/cloud-text-speech-python3

# NOTE: The "serivce account" JSON was copied into this Python script for demonstration purposes.
#       You could also just set GOOGLE_APPLICATION_CREDENTIALS to point to your service account .json file and
#       and remove the following.
#       If you do copy and paste into this script, be sure to add an extra backslash to the \n in "private_key".
gcp_service_account_json_path = f'{tempfile.gettempdir()}/gcp_key.json'
with open(gcp_service_account_json_path, 'w') as f:
    f.write("""{
  "type": "service_account",
  "project_id": "keyword-generator-367517",
  "private_key_id": "2af4482dd0beb3c0b2e54739a9968b43bacecf84",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDb96LjLhQMcF4O\\n2mmpViIHIlZ6vgW+PfLJ/AZSuWlUMR7JxumW4CHeciyPW3bmjUs9U6eXf1hPqOdd\\nSEPjWS4yR/Spl+1WmUn4Z9Ky+cLMjRHD9OI6/MCAjubwYtQBcRYRmjjXHBgoDpDC\\nmAWi8cDbfrnp/SiSyzUfSePAlfsPXc2zpgDfje0ZmpBzzMDODaajt8lgxd8QG7BX\\nDUcjm4PGSKzfTdkAkh5NZDXUFk/PotkYrYwC1vHoNWSL8XpUMIEQqJU8TZuecfoj\\n2N6Go0i+WguYQeH/wLRRKLwWNkFs8Ax1VyglIztQeTxjF3CtME0a4k2nqmlCKyYp\\nvbBbvct3AgMBAAECggEABg7xcMPaRoIEuWkBAdPg3nXYRQfSCH9QWmtJ9pbJnDLu\\nBnpjppDzeSY8LJmQdB1wMUYgxbD6tG3KpB93B3EvvgojIt086rWnHWeDlRMA2LXV\\nXfzcdLyTNvkeQwhDcRh9DrvR7z+5GzCf+vIyxNaTcgkh4VD7D2v3qttE3fiYO7EI\\nh4+0bghVOg5EILfb/tPMj5brGAP3ClftzZvj7WIkZeRLUrGgGDD0dLKygLkHer+O\\nmhT/5QlV7LTvJVk5z+i7A3xMoMOF+fjp2siw9YzC44tvQNX7jHyhL+2CFy6YV7Jv\\nS4gjsk4T7WOxyvDJhA/Xh+OQr4MVKfcgbo0YS6ppxQKBgQD6B1g7cqMVFYgLFNoT\\n7U+1mLoISXoAnRJPBnNrKbNS0ZeC4zdtbJKBDogQxHjwcmPgv7eCXzNofBVopl4R\\nyvl6ZKcDdr1fRgczqPtsE3QyptkdQclKIYA0pU4+7ZwLlwJAodYURT3zzTdTrXk5\\nEjOK7gslmdr5ZtHQvnYO65ZXrQKBgQDhOH+2PL4hwZPthOz+Kd/A81aj/zLO0TjF\\nWuw1ibrBJ5WfnDQxJZWLjMJSFdvfVMXgTQENpq9CeFI2FJWTVORNbMc987XhqBnx\\nQAAxfRjfy7smZ3LJUMav8C6Dla+jo2/jpjvFiUFaoFbrV+BeVkN90NCvOVZ9GjdE\\nsAUXEQ4kMwKBgFiGaTMDL8KzUOu7gksz5tkBLjzo5w14j5bzTcJPjXJxSxfIo0NX\\nAbg4EOz+42Me3UYiGzNJycXgySO4Y+4g05wGLywGyp4FCV+9IOfvK2ETuiOlu0NI\\nAUCilsWpE2r3GJERu96JdZnwuvohnZ4bV6yFA+VYSDOtt/QUu3Ak8aIxAoGBAKIk\\nmN1MUd3fjW48eppo7yvshH3A5oU631JGKTRKGeehZfjo7jJLyqQTDHsoPYlFcMgQ\\n6Cc5z4ddNGK24xCU12BeZfrWECWLblHfL8RxOY01EWGOrHb+7mwP0IzvIOoAajdM\\noE+QhzqFoM4CEAgatrBHu1XLQ9cBHrUWvDNlFfc9AoGAcOxBYgjctK9+1nRAyuzT\\na48ovP940W7QeBnXqbwDlu80Ve79/Dw34eP26MsEehKCAQ9OhZv+dVvBGeL2Z45P\\nIabgZpEmnfsMIcTZfSCCHeSit+s2JMSPn/SdTjSHe270pX8TZ9lPqABRZ3Pbpwtr\\nnR7FEx0B78HJADj9CYmoSUo=\\n-----END PRIVATE KEY-----\\n",
  "client_email": "my-tts-sa@keyword-generator-367517.iam.gserviceaccount.com",
  "client_id": "118369428326213488735",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/my-tts-sa%40keyword-generator-367517.iam.gserviceaccount.com"
}""")


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcp_service_account_json_path
with open(os.environ['GOOGLE_APPLICATION_CREDENTIALS'], 'r') as f:
    credentials = json.load(f)
os.environ['PROJECT_ID'] = credentials['project_id']


###################################################################################################
# Configure your AWS credentials
# See: https://docs.aws.amazon.com/polly/latest/dg/get-started-what-next.html
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIATZWWZR5TWBUNF6IX'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'v0IRHPUGeNwj1CA7saVduF1uxW84bgkzQpOWLfdr'
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'




###################################################################################################
# Define the directory where the dataset will be generated
OUT_DIR = f'{tempfile.gettempdir()}/alexa_dataset'.replace('\\', '/')


###################################################################################################
# Define the keywords and corresponding aliases to generate
# For the _unknown_ class (e.g. negative class), we want words that sound similar to "alexa".
# NOTE: If the base word starts with an underscore, it is not included in the generation list.
# So the generation list will be:
# alexa, ehlexa, eelexa, aalexa
# ah, aag, a, o, uh, ...
#
# The dataset will have the directory structure:
# $TEMP/alexa_dataset/alexa/sample1.wav
# $TEMP/alexa_dataset/alexa/sample2.wav
# $TEMP/alexa_dataset/alexa/...
# $TEMP/alexa_dataset/_unknown_/sample1.wav
# $TEMP/alexa_dataset/_unknown_/sample2.wav
# $TEMP/alexa_dataset/_unknown_/...
KEYWORDS = [
    Keyword('alexa',
        max_count=100, # In practice, the max count should be much larger (e.g. 10000)
        aliases=('ehlexa', 'eelexa', 'aalexa')
    ),
    Keyword('_unknown_',
        max_count=200, # In practice, the max count should be much larger (e.g. 20000)
        aliases=(
        'ah', 'aah', 'a', 'o', 'uh', 'ee', 'aww', 'ala',
        'alex', 'lex', 'lexa', 'lexus', 'alexus', 'exus', 'exa',
        'alert', 'alec', 'alef', 'alee', 'ales', 'ale',
        'aleph', 'alefs', 'alevin', 'alegar', 'alexia',
        'alexin', 'alexine', 'alencon', 'alexias',
        'aleuron', 'alembic', 'alice', 'aleeyah'
    ))
]


###################################################################################################
# Define the augmentations to apply the keywords
AUGMENTATIONS = [
    Augmentation(rate=VoiceRate.xslow, pitch=VoicePitch.low),
    Augmentation(rate=VoiceRate.xslow, pitch=VoicePitch.medium),
    Augmentation(rate=VoiceRate.xslow, pitch=VoicePitch.high),
    Augmentation(rate=VoiceRate.medium, pitch=VoicePitch.low),
    Augmentation(rate=VoiceRate.medium, pitch=VoicePitch.medium),
    Augmentation(rate=VoiceRate.medium, pitch=VoicePitch.high),
    Augmentation(rate=VoiceRate.xfast, pitch=VoicePitch.low),
    Augmentation(rate=VoiceRate.xfast, pitch=VoicePitch.medium),
    Augmentation(rate=VoiceRate.xfast, pitch=VoicePitch.high),
]


###################################################################################################
# Instantiate the AudioDatasetGenerator
with AudioDatasetGenerator(
    out_dir=OUT_DIR,
    n_jobs=8 # We want to generate the keywords across 8 parallel jobs
) as generator:
    # Load the cloud backends, installing the Python packages if necessary
    generator.load_backend('aws', install_python_package=True)
    generator.load_backend('gcp', install_python_package=True)
    generator.load_backend('azure', install_python_package=True)

    print('Listing voices ...')
    voices = generator.list_voices()

    # Generate a list of all possible configurations, randomly shuffle, then truncate
    # based on the "max_count" specified for each keyword
    print('Listing configurations ...')
    all_configurations = generator.list_configurations(
        keywords=KEYWORDS,
        augmentations=AUGMENTATIONS,
        voices=voices,
        truncate=True,
        seed=42
    )
    n_configs = sum(len(x) for x in all_configurations.values())

    # Print a summary of the configurations
    print(generator.get_summary(all_configurations))


    input(
        '\nWARNING: Running this script is NOT FREE!\n\n'
        'Each cloud backend charges a different rate per character.\n'
        'The character counts are listed above.\n\n'
        'Refer to each backend\'s docs for the latest pricing:\n'
        '- AWS: https://aws.amazon.com/polly/pricing\n'
        '- Azure: https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services\n'
        '- Google: https://cloud.google.com/text-to-speech/pricing\n'
        '\nPress "enter" to continue and generate the dataset\n'
    )

    # Generate the dataset (with pretty progress bars)
    print(f'Generating keywords at: {generator.out_dir}\n')
    with tqdm.tqdm(total=n_configs, desc='Overall'.rjust(10), unit='word', position=1) as pb_outer:
        for keyword, config_list in all_configurations.items():
            with tqdm.tqdm(desc=keyword.value.rjust(10), total=len(config_list), unit='word', position=0) as pb_inner:
                for config in config_list:
                    generator.generate(
                        config,
                        on_finished=lambda _: (pb_inner.update(1), pb_outer.update(1))
                    )
                generator.join() # Wait for the current keyword to finish before continuing to the next

