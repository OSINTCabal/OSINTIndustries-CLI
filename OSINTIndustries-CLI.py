import requests
import json
import sys
import time
import os
import threading
import re
from colorama import Fore, Back, Style, init
from typing import Dict, Any, List

# Initialize colorama
init(autoreset=True)

class LoadingAnimation:
    def __init__(self, message="Loading..."):
        self.message = message
        self.is_running = False
        self.animation_thread = None
        self.animation_frames = [
            "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
        ]

    def animate(self):
        i = 0
        while self.is_running:
            frame = self.animation_frames[i % len(self.animation_frames)]
            sys.stdout.write(f"\r{Fore.CYAN}{frame} {self.message}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

    def start(self):
        self.is_running = True
        self.animation_thread = threading.Thread(target=self.animate)
        self.animation_thread.daemon = True
        self.animation_thread.start()

    def stop(self):
        self.is_running = False
        if self.animation_thread:
            self.animation_thread.join(0.5)
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

class OSINTSearchTool:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.osint.industries"
        self.headers = {
            "api-key": self.api_key,
            "accept": "application/json"
        }

    def check_credits(self):
        """Check remaining API credits"""
        loader = LoadingAnimation("Checking API credits...")
        loader.start()

        url = f"{self.base_url}/misc/credits"
        try:
            response = requests.get(url, headers=self.headers)
            loader.stop()

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict):
                    return result
                else:
                    return {"credits": result, "error": False}
            else:
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": response.text
                }
        except Exception as e:
            loader.stop()
            return {"error": True, "message": str(e)}

    def search(self, search_type, query):
        """Perform a search using the OSINT Industries API"""
        url = f"{self.base_url}/v2/request"

        type_mapping = {
            "username": "username",
            "email": "email",
            "phone": "phone",
            "person": "name",
            "crypto": "crypto"
        }

        api_type = type_mapping.get(search_type)
        if not api_type:
            return {"error": True, "message": f"Invalid search type: {search_type}"}

        loader = LoadingAnimation(f"Searching for {search_type}: {query}...")
        loader.start()

        try:
            response = requests.get(url, headers=self.headers, params={"type": search_type, "query": query})
            loader.stop()

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 451:
                return {
                    "error": True,
                    "status_code": 451,
                    "message": "Unavailable for Legal Reasons",
                    "details": response.text or "No additional details provided."
                }
            else:
                try:
                    error_json = response.json()
                    error_message = error_json.get('message', response.text)
                except:
                    error_message = response.text

                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": error_message
                }
        except Exception as e:
            loader.stop()
            return {"error": True, "message": str(e)}

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print a banner for the tool"""
    art = """
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@%%%%%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@%:..     ...#@@@@@@@@@@*:.....:*@@@@@@:...+@@@@=....+@@@@@%....#@@+...............%@@@@@@@
@@@@@@@@#:             .=@@@@@@+.         .+@@@@:   =@@@@=    .*@@@@%   .#@@+.              %@@@@@@@
@@@@@@@-   ..*@@@@@%:.   .%@@@+   .*@@@%-.+@@@@@:   =@@@@=      *@@@%   .#@@@@@@@%:   =@@@@@@@@@@@@@
@@@@@@+.  .#@@@@@@@@@%.   :@@@-   .#@@@@@@@@@@@@:   =@@@@=   =. .*@@%   .#@@@@@@@%:   =@@@@@@@@@@@@@
@@@@@@.  .#@@@:   .#@@@.   *@@@.     .*%@@@@@@@@:   =@@@@=   ++.  %@%   .#@@@@@@@%:   =@@@@@@@@@@@@@
@@@@@#   :%@@-     .@@@=   =@@@@=.      .:+@@@@@:   =@@@@=   :@:   *@.  .#@@@@@@@%:   =@@@@@@@@@@@@@
@@@@@@.  .#@@%.   .+@@@:   *@@@@@@@+:..    .@@@@:   =@@@@=   :@@:  .#.  .#@@@@@@@%:   =@@@@@@@@@@@@@
@@@@@@=   .@@@@%%%@@@@:   .@@@@@@@@@@@@*    *@@@:   =@@@@=   :@@@-. ::  .#@@@@@@@%:   =@@@@@@@@@@@@@
@@@@@@@- -%@@@@@@@@%=.   .#@@@@=.+%@@@@*   .%@@@:   =@@@@=   :@@@@:     .#@@@@@@@%:   =@@@@@@@@@@@@@
@@@@@@@@%@@@*......     -@@@@#.   .....   .+@@@@:   =@@@@=   :@@@@@:    .#@@@@@@@%:   =@@@@@@@@@@@@@
@@@@@@@@@@@=.       ..=%@@@@@@@*-.     ..=%@@@@@:   =@@@@=   :@@@@@%:   .#@@@@@@@%:   =@@@@@@@@@@@@@
@@@@@@@@@@@@@@@%##%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

                        OSINT Industries Search Tool
                              v2.0 Enhanced
    """
    print(f"{Fore.CYAN}{art}{Style.RESET_ALL}")

def print_box(title, content, width=80, color=Fore.CYAN):
    """Print content in a nice box"""
    print(f"\n{color}╔{'═' * (width - 2)}╗{Style.RESET_ALL}")
    print(f"{color}║{Style.RESET_ALL} {title.center(width - 4)} {color}║{Style.RESET_ALL}")
    print(f"{color}╠{'═' * (width - 2)}╣{Style.RESET_ALL}")

    for line in content:
        if len(line) > width - 6:
            # Wrap long lines
            words = line.split()
            current_line = ""
            for word in words:
                if len(current_line + word) < width - 6:
                    current_line += word + " "
                else:
                    print(f"{color}║{Style.RESET_ALL} {current_line.ljust(width - 4)} {color}║{Style.RESET_ALL}")
                    current_line = word + " "
            if current_line:
                print(f"{color}║{Style.RESET_ALL} {current_line.ljust(width - 4)} {color}║{Style.RESET_ALL}")
        else:
            print(f"{color}║{Style.RESET_ALL} {line.ljust(width - 4)} {color}║{Style.RESET_ALL}")

    print(f"{color}╚{'═' * (width - 2)}╝{Style.RESET_ALL}")

def print_section_header(title, icon="●"):
    """Print a styled section header"""
    print(f"\n{Fore.YELLOW}{'─' * 80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{icon} {title}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'─' * 80}{Style.RESET_ALL}")

def format_social_media_result(data: Dict[str, Any]) -> List[str]:
    """Format social media results nicely"""
    lines = []

    if isinstance(data, dict):
        for platform, info in data.items():
            if isinstance(info, dict):
                lines.append(f"{Fore.MAGENTA}▸ {platform.upper()}{Style.RESET_ALL}")

                # Handle nested data
                for key, value in info.items():
                    if isinstance(value, (str, int, float, bool)):
                        if key.lower() in ['url', 'link', 'profile']:
                            lines.append(f"  {Fore.GREEN}🔗 {key}:{Style.RESET_ALL} {Fore.CYAN}{value}{Style.RESET_ALL}")
                        else:
                            lines.append(f"  {Fore.YELLOW}{key}:{Style.RESET_ALL} {value}")
                    elif isinstance(value, list) and value:
                        lines.append(f"  {Fore.YELLOW}{key}:{Style.RESET_ALL}")
                        for item in value[:5]:  # Limit to first 5 items
                            lines.append(f"    • {item}")
                        if len(value) > 5:
                            lines.append(f"    ... and {len(value) - 5} more")

                lines.append("")  # Empty line between platforms

    return lines

def format_data_breach_results(data: List[Dict[str, Any]]) -> List[str]:
    """Format data breach results"""
    lines = []

    if not data:
        lines.append(f"{Fore.GREEN}✓ No data breaches found{Style.RESET_ALL}")
        return lines

    lines.append(f"{Fore.RED}⚠ Found {len(data)} breach(es):{Style.RESET_ALL}\n")

    for i, breach in enumerate(data[:10], 1):  # Limit to 10 breaches
        lines.append(f"{Fore.MAGENTA}[{i}] {breach.get('name', 'Unknown Breach')}{Style.RESET_ALL}")

        if 'date' in breach:
            lines.append(f"    {Fore.YELLOW}Date:{Style.RESET_ALL} {breach['date']}")
        if 'description' in breach:
            desc = breach['description']
            if len(desc) > 100:
                desc = desc[:97] + "..."
            lines.append(f"    {Fore.YELLOW}Info:{Style.RESET_ALL} {desc}")
        if 'data_classes' in breach:
            lines.append(f"    {Fore.YELLOW}Exposed:{Style.RESET_ALL} {', '.join(breach['data_classes'][:5])}")

        lines.append("")

    if len(data) > 10:
        lines.append(f"{Fore.CYAN}... and {len(data) - 10} more breaches{Style.RESET_ALL}")

    return lines

def format_person_info(data: Dict[str, Any]) -> List[str]:
    """Format person information"""
    lines = []

    # Basic Info
    if 'name' in data:
        lines.append(f"{Fore.GREEN}👤 Name:{Style.RESET_ALL} {data['name']}")
    if 'age' in data:
        lines.append(f"{Fore.GREEN}📅 Age:{Style.RESET_ALL} {data['age']}")
    if 'location' in data:
        lines.append(f"{Fore.GREEN}📍 Location:{Style.RESET_ALL} {data['location']}")
    if 'occupation' in data:
        lines.append(f"{Fore.GREEN}💼 Occupation:{Style.RESET_ALL} {data['occupation']}")

    # Contact Info
    if 'email' in data or 'phone' in data:
        lines.append(f"\n{Fore.YELLOW}Contact Information:{Style.RESET_ALL}")
        if 'email' in data:
            lines.append(f"  📧 {data['email']}")
        if 'phone' in data:
            lines.append(f"  📱 {data['phone']}")

    return lines

def extract_useful_data(data: Any, key_path: str = "") -> Dict[str, Any]:
    """Extract useful non-null data from nested structures"""
    result = {}

    if isinstance(data, dict):
        for key, value in data.items():
            if value is None or value == "" or value == [] or value == {}:
                continue

            if isinstance(value, (dict, list)):
                nested = extract_useful_data(value, f"{key_path}.{key}")
                if nested:
                    result[key] = nested
            else:
                result[key] = value
    elif isinstance(data, list):
        cleaned_list = []
        for item in data:
            if isinstance(item, (dict, list)):
                nested = extract_useful_data(item, key_path)
                if nested:
                    cleaned_list.append(nested)
            elif item is not None and item != "" and item != []:
                cleaned_list.append(item)
        return cleaned_list if cleaned_list else None
    else:
        return data

    return result if result else None

def format_nested_dict(data: Dict[str, Any], indent: int = 0, max_depth: int = 4) -> List[str]:
    """Format nested dictionary data with intelligent display"""
    lines = []
    indent_str = "  " * indent

    # Extract only useful data first
    if indent == 0:
        data = extract_useful_data(data) or {}

    if indent > max_depth:
        return lines

    for key, value in data.items():
        # Skip empty values
        if value is None or value == "" or value == [] or value == {}:
            continue

        # Format key
        formatted_key = key.replace('_', ' ').title()

        if isinstance(value, dict):
            # Check if dict has actual useful content
            if value:
                lines.append(f"{indent_str}{Fore.MAGENTA}▸ {formatted_key}:{Style.RESET_ALL}")
                lines.extend(format_nested_dict(value, indent + 1, max_depth))
        elif isinstance(value, list):
            if not value:
                continue

            lines.append(f"{indent_str}{Fore.MAGENTA}▸ {formatted_key}:{Style.RESET_ALL}")
            if all(isinstance(item, (str, int, float, bool)) for item in value):
                # Simple list
                for item in value[:10]:
                    lines.append(f"{indent_str}  • {item}")
                if len(value) > 10:
                    lines.append(f"{indent_str}  {Fore.CYAN}... and {len(value) - 10} more{Style.RESET_ALL}")
            else:
                # Complex list
                for i, item in enumerate(value[:5], 1):
                    if isinstance(item, dict):
                        # Only show if there's actual data
                        item_data = extract_useful_data(item)
                        if item_data:
                            lines.append(f"{indent_str}  {Fore.YELLOW}[{i}]{Style.RESET_ALL}")
                            lines.extend(format_nested_dict(item_data, indent + 2, max_depth))
                    else:
                        lines.append(f"{indent_str}  • {item}")
                if len(value) > 5:
                    lines.append(f"{indent_str}  {Fore.CYAN}... and {len(value) - 5} more items{Style.RESET_ALL}")
        elif isinstance(value, str):
            # Check if it's a URL
            if value.startswith(('http://', 'https://')):
                lines.append(f"{indent_str}{Fore.YELLOW}{formatted_key}:{Style.RESET_ALL} {Fore.CYAN}🔗 {value}{Style.RESET_ALL}")
            else:
                # Truncate long strings
                display_value = value if len(value) < 100 else value[:97] + "..."
                lines.append(f"{indent_str}{Fore.YELLOW}{formatted_key}:{Style.RESET_ALL} {display_value}")
        elif isinstance(value, bool):
            icon = "✓" if value else "✗"
            color = Fore.GREEN if value else Fore.RED
            lines.append(f"{indent_str}{Fore.YELLOW}{formatted_key}:{Style.RESET_ALL} {color}{icon}{Style.RESET_ALL}")
        else:
            lines.append(f"{indent_str}{Fore.YELLOW}{formatted_key}:{Style.RESET_ALL} {value}")

    return lines

def format_platform_result(item: Dict[str, Any]) -> List[str]:
    """Format individual platform result"""
    lines = []

    # Platform name and category
    module = item.get('module', 'Unknown')
    status = item.get('status', 'unknown')

    # Status indicator
    status_icon = "✓" if status == "found" else "✗" if status == "not_found" else "?"
    status_color = Fore.GREEN if status == "found" else Fore.RED if status == "not_found" else Fore.YELLOW

    lines.append(f"\n{Fore.CYAN}╔{'═' * 78}╗{Style.RESET_ALL}")

    # Big platform name
    platform_name = module.upper()
    lines.append(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{platform_name}{Style.RESET_ALL}  {status_color}{status_icon} {status.upper()}{Style.RESET_ALL}")

    # Category
    if 'category' in item:
        cat = item['category']
        if isinstance(cat, dict):
            cat_name = cat.get('name', 'Unknown')
            lines.append(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Category:{Style.RESET_ALL} {cat_name}")

    lines.append(f"{Fore.CYAN}╚{'═' * 78}╝{Style.RESET_ALL}")

    # Extract spec_format data (actual user data)
    if 'spec_format' in item and isinstance(item['spec_format'], list) and item['spec_format']:
        spec_data = item['spec_format'][0] if item['spec_format'] else {}

        if spec_data:
            lines.append(f"\n{Fore.GREEN}╔═══ ACCOUNT DETAILS ═══╗{Style.RESET_ALL}")

            # Define important fields to show
            important_fields = [
                ('id', '🆔 ID'),
                ('username', '👤 Username'),
                ('name', '📝 Name'),
                ('first_name', '📝 First Name'),
                ('last_name', '📝 Last Name'),
                ('email', '📧 Email'),
                ('phone', '📱 Phone'),
                ('picture_url', '🖼️ Picture'),
                ('profile_url', '🔗 Profile'),
                ('followers', '👥 Followers'),
                ('following', '➕ Following'),
                ('verified', '✓ Verified'),
                ('private', '🔒 Private'),
                ('registered', '📅 Registered'),
                ('created_at', '📅 Created'),
                ('last_seen', '👁️ Last Seen'),
            ]

            for field_key, display_name in important_fields:
                if field_key in spec_data:
                    value = spec_data[field_key]

                    if value is None or value == "" or value == []:
                        continue

                    if isinstance(value, dict):
                        # Extract actual value from nested dict
                        actual_value = value.get('value', value.get('data', None))
                        if actual_value and actual_value != "":
                            if isinstance(actual_value, str) and actual_value.startswith(('http://', 'https://')):
                                lines.append(f"  {display_name}: {Fore.CYAN}{actual_value}{Style.RESET_ALL}")
                            elif isinstance(actual_value, bool):
                                icon = "✓" if actual_value else "✗"
                                color = Fore.GREEN if actual_value else Fore.RED
                                lines.append(f"  {display_name}: {color}{icon}{Style.RESET_ALL}")
                            else:
                                lines.append(f"  {display_name}: {actual_value}")
                    elif isinstance(value, bool):
                        icon = "✓" if value else "✗"
                        color = Fore.GREEN if value else Fore.RED
                        lines.append(f"  {display_name}: {color}{icon}{Style.RESET_ALL}")
                    elif isinstance(value, str):
                        if value.startswith(('http://', 'https://')):
                            lines.append(f"  {display_name}: {Fore.CYAN}{value}{Style.RESET_ALL}")
                        else:
                            lines.append(f"  {display_name}: {value}")
                    else:
                        lines.append(f"  {display_name}: {value}")

    # Show image if available from front_schemas
    if 'front_schemas' in item and isinstance(item['front_schemas'], list):
        for schema in item['front_schemas'][:1]:  # Just first one
            if isinstance(schema, dict) and 'image' in schema:
                image_url = schema['image']
                if image_url:
                    lines.append(f"\n{Fore.YELLOW}🖼️ Profile Image:{Style.RESET_ALL} {Fore.CYAN}{image_url}{Style.RESET_ALL}")

    # Reliable source indicator
    if 'reliable_source' in item:
        is_reliable = item['reliable_source']
        if is_reliable:
            lines.append(f"\n{Fore.GREEN}✓ Verified/Reliable Source{Style.RESET_ALL}")

    return lines

def display_results(results: Dict[str, Any], search_type: str, query: str):
    """Display search results with intelligent formatting"""

    if isinstance(results, dict) and results.get("error"):
        # Error display
        print_section_header("ERROR", "✗")
        error_lines = [
            f"{Fore.RED}{results.get('message', 'Unknown error')}{Style.RESET_ALL}",
        ]

        if "status_code" in results:
            status_code = results['status_code']
            error_lines.append(f"Status Code: {status_code}")

            hints = {
                401: "This indicates an authentication error. Check your API key.",
                429: "You've exceeded the API rate limits. Try again later.",
                451: "The requested information cannot be provided due to legal reasons.",
                400: "Bad request. Check your search parameters."
            }

            if status_code in hints:
                error_lines.append(f"\n{Fore.YELLOW}💡 Hint:{Style.RESET_ALL} {hints[status_code]}")

        if "details" in results and results["details"]:
            error_lines.append(f"\n{Fore.CYAN}Details:{Style.RESET_ALL}")
            error_lines.append(results['details'])

        print_box("Error Information", error_lines, color=Fore.RED)
        return

    # Success display
    print(f"\n{Fore.CYAN}{'═' * 80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}SEARCH RESULTS: {search_type.upper()}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 78}╝{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}Target:{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{query}{Style.RESET_ALL}\n")

    # Handle list results (typical OSINT Industries response format)
    if isinstance(results, list):
        # Count found vs not found
        found_count = sum(1 for item in results if isinstance(item, dict) and item.get('status') == 'found')
        not_found_count = len(results) - found_count

        print(f"\n{Fore.CYAN}╔═══ SUMMARY ═══╗{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   ✓ Found on {found_count} platform(s){Style.RESET_ALL}")
        print(f"{Fore.RED}   ✗ Not found on {not_found_count} platform(s){Style.RESET_ALL}")
        print(f"{Fore.CYAN}   📝 Total platforms checked: {len(results)}{Style.RESET_ALL}")

        # Separate found and not found
        found_results = [item for item in results if isinstance(item, dict) and item.get('status') == 'found']
        not_found_results = [item for item in results if isinstance(item, dict) and item.get('status') != 'found']

        # Display found results
        if found_results:
            print(f"\n{Fore.GREEN}{'═' * 80}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}✓ FOUND ON {len(found_results)} PLATFORM(S){Style.RESET_ALL}")
            print(f"{Fore.GREEN}╚{'═' * 78}╝{Style.RESET_ALL}")

            for i, item in enumerate(found_results, 1):
                print(f"\n{Fore.YELLOW}{'─' * 80}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{Style.BRIGHT}[{i}/{len(found_results)}]{Style.RESET_ALL}")
                lines = format_platform_result(item)
                for line in lines:
                    print(line)

        # Optionally show not found (collapsed)
        if not_found_results:
            print(f"\n{Fore.YELLOW}{'─' * 80}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}❌ Not found on:{Style.RESET_ALL} ", end="")
            not_found_names = [item.get('module', 'Unknown').title() for item in not_found_results[:10]]
            print(", ".join(not_found_names), end="")
            if len(not_found_results) > 10:
                print(f" and {len(not_found_results) - 10} more", end="")
            print()

    elif isinstance(results, dict):
        # Handle dict results
        total_items = len(results)
        print(f"{Fore.GREEN}📊 Found {total_items} data point(s){Style.RESET_ALL}")

        print_section_header("Detailed Information", "📋")
        lines = format_nested_dict(results)
        for line in lines:
            print(line)

    # Footer
    print(f"\n{Fore.YELLOW}{'─' * 80}{Style.RESET_ALL}")

    # Save option
    save = input(f"\n{Fore.CYAN}💾 Save results to file? (y/n):{Style.RESET_ALL} ").lower()
    if save == 'y':
        filename = input(f"{Fore.CYAN}📁 Enter filename (default: results_{int(time.time())}.json):{Style.RESET_ALL} ")
        if not filename:
            filename = f"results_{int(time.time())}.json"
        if not filename.endswith('.json'):
            filename += '.json'

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"{Fore.GREEN}✓ Results saved to {filename}{Style.RESET_ALL}")

def print_menu(credits_info):
    """Print the main menu"""
    # Display credits
    if isinstance(credits_info, dict) and not credits_info.get("error"):
        credits = credits_info.get('credits', 'Unknown')
        credit_color = Fore.GREEN if isinstance(credits, int) and credits > 100 else Fore.YELLOW if isinstance(credits, int) and credits > 50 else Fore.RED
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  💳 API Credits: {credit_color}{str(credits).ljust(62)}{Style.RESET_ALL}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    elif isinstance(credits_info, int):
        credit_color = Fore.GREEN if credits_info > 100 else Fore.YELLOW if credits_info > 50 else Fore.RED
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  💳 API Credits: {credit_color}{str(credits_info).ljust(62)}{Style.RESET_ALL}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}⚠ Unable to fetch credit information{Style.RESET_ALL}")

    # Menu options
    print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}                           {'SEARCH OPTIONS'.center(50)}                      {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╠══════════════════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.MAGENTA}[1]{Style.RESET_ALL} 👤 Username Search              {Fore.MAGENTA}[4]{Style.RESET_ALL} 👥 Person Search (Name)     {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.MAGENTA}[2]{Style.RESET_ALL} 📧 Email Search                 {Fore.MAGENTA}[5]{Style.RESET_ALL} 💰 Cryptocurrency Wallet    {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.MAGENTA}[3]{Style.RESET_ALL} 📱 Phone Number Search          {Fore.RED}[0]{Style.RESET_ALL} 🚪 Exit                     {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")

def main():
    # Your API key
    API_KEY = "YOUR KEY HERE"

    # Initialize the search tool
    search_tool = OSINTSearchTool(API_KEY)

    while True:
        clear_screen()
        print_banner()

        # Check and display credits
        credits = search_tool.check_credits()
        print_menu(credits)

        choice = input(f"\n{Fore.GREEN}➤ Enter your choice (0-5):{Style.RESET_ALL} ")

        if choice == '0':
            print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}  {'Thank you for using OSINT Industries Search Tool!'.center(76)}  {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
            sys.exit(0)

        elif choice in ['1', '2', '3', '4', '5']:
            search_types = {
                '1': ('username', '👤 Username'),
                '2': ('email', '📧 Email'),
                '3': ('phone', '📱 Phone'),
                '4': ('person', '👥 Person'),
                '5': ('crypto', '💰 Crypto Wallet')
            }

            search_type, display_name = search_types[choice]
            query = input(f"\n{Fore.CYAN}➤ Enter {display_name} to search:{Style.RESET_ALL} ")

            if not query.strip():
                print(f"\n{Fore.RED}✗ Search query cannot be empty.{Style.RESET_ALL}")
                time.sleep(2)
                continue

            # Confirm search
            confirm = input(f"{Fore.YELLOW}➤ Search for '{query}'? (y/n):{Style.RESET_ALL} ").lower()
            if confirm != 'y':
                continue

            print()  # Empty line for better spacing

            # Perform the search
            results = search_tool.search(search_type, query)
            display_results(results, search_type, query)

            input(f"\n{Fore.CYAN}Press Enter to return to main menu...{Style.RESET_ALL}")

        else:
            print(f"\n{Fore.RED}✗ Invalid choice. Please select 0-5.{Style.RESET_ALL}")
            time.sleep(1.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}╔══════════════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}║{Style.RESET_ALL}  {'Operation cancelled by user'.center(76)}  {Fore.YELLOW}║{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        sys.exit(0)
