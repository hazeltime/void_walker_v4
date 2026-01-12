"""
UI Banner component for Void Walker.
Handles all banner and header displays.
"""
import os
from common.constants import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION, APP_TAGLINE,
    REPOSITORY_URL, RELEASE_DATE, Color
)


class Banner:
    """Displays application banners and headers"""
    
    @staticmethod
    def clear():
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_ascii_banner():
        """Display ASCII art banner with version and description"""
        Banner.clear()
        print(f"{Color.CYAN}{'='*70}")
        print("  ██╗   ██╗ ██████╗ ██╗██╗███╗   ██╗  ██╗    ██╗ █████╗ ██╗     ██╗  ██╗███████╗██████╗ ")
        print("  ██║   ██║██╔═══██╗██║██║████╗  ██║  ██║    ██║██╔══██╗██║     ██║ ██╔╝██╔════╝██╔══██╗")
        print("  ██║   ██║██║   ██║██║██║██╔██╗ ██║  ██║ █╗ ██║███████║██║     █████╔╝ █████╗  ██████╔╝")
        print("  ╚██╗ ██╔╝██║   ██║██║██║██║╚██╗██║  ██║███╗██║██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗")
        print("   ╚████╔╝ ╚██████╔╝██║██║██║ ╚████║  ╚███╔███╔╝██║  ██║███████╗██║  ██╗███████╗██║  ██║")
        print("    ╚═══╝   ╚═════╝ ╚═╝╚═╝╚═╝  ╚═══╝   ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝")
        print("="*70)
        print(f"  {Color.YELLOW}{APP_VERSION}{Color.RESET} | {APP_DESCRIPTION}")
        print(f"  {Color.GRAY}{APP_TAGLINE}{Color.RESET}")
        print(f"{'='*70}{Color.RESET}\n")
    
    @staticmethod
    def print_header(title=None):
        """Display simple header"""
        Banner.clear()
        title_text = f"  {title}" if title else f"  {APP_NAME} v{APP_VERSION} - ENTERPRISE CONSOLE"
        print(f"{Color.CYAN}{'='*70}")
        print(title_text)
        print(f"{'='*70}{Color.RESET}")
    
    @staticmethod
    def print_section_header(text, width=70):
        """Display section header with box"""
        print(f"\n{Color.CYAN}╔{'═' * (width-2)}╗{Color.RESET}")
        # Center text
        padding = (width - len(text) - 2) // 2
        print(f"{Color.CYAN}║{Color.RESET}{' ' * padding}{Color.YELLOW}{text}{Color.RESET}{' ' * (width - len(text) - padding - 2)}{Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}╚{'═' * (width-2)}╝{Color.RESET}\n")
    
    @staticmethod
    def print_about():
        """Display about screen with features and performance"""
        Banner.print_header("ABOUT VOID WALKER")
        
        print(f"\n{Color.CYAN}╔═══ ABOUT VOID WALKER ═════════════════════════════════════════════╗{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}                                                                   {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}  {Color.YELLOW}Version:{Color.RESET} {APP_VERSION}                                                  {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}  {Color.YELLOW}Release Date:{Color.RESET} {RELEASE_DATE}                                     {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}  {Color.YELLOW}Repository:{Color.RESET} {REPOSITORY_URL}                {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}                                                                   {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}  {Color.GREEN}⚡ KEY FEATURES:{Color.RESET}                                                {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}    • Concurrent multi-threaded scanning (up to 32 workers)       {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}    • Intelligent SSD/HDD detection and optimization              {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}    • BFS (breadth-first) and DFS (depth-first) strategies       {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}    • Advanced filtering: patterns, depth limits, exclusions     {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}    • Resume capability for interrupted scans                     {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}    • Real-time dashboard with live metrics                       {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}    • SQLite persistence with session history                     {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}    • Dry-run mode for safe testing                               {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}                                                                   {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}  {Color.GREEN}📊 PERFORMANCE:{Color.RESET}                                                {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}    • SSD: 10-12x faster with 16 threads + BFS                    {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}    • HDD: 3-4x faster with 4 threads + DFS                       {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}    • Average scan rate: 200-500 folders/second (SSD)             {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}║{Color.RESET}                                                                   {Color.CYAN}║{Color.RESET}")
        print(f"{Color.CYAN}╚═══════════════════════════════════════════════════════════════════╝{Color.RESET}\n")
        input("Press Enter to return to main menu...")
