import sys
from pathlib import Path
from types import SimpleNamespace

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if 'cloakbrowser' not in sys.modules:
	sys.modules['cloakbrowser'] = SimpleNamespace(
		launch_async=None,
		launch_persistent_context_async=None,
	)

