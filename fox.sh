#!/bin/bash

# ============================================================
#  ███████╗ ██████╗ ██╗  ██╗
#  ██╔════╝██╔═══██╗╚██╗██╔╝
#  █████╗  ██║   ██║ ╚███╔╝
#  ██╔══╝  ██║   ██║ ██╔██╗
#  ██║     ╚██████╔╝██╔╝ ██╗
#  ╚═╝      ╚═════╝ ╚═╝  ╚═╝
#
#  FOX OPERATION MANAGER
#  Usage: source fox.sh  (atau ./fox.sh <command>)
# ============================================================

FOX_HOME="/root/fox"
OPS_DIR="$FOX_HOME/operations"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

banner() {
    echo -e "${RED}"
    echo '  ______  ____   __  __'
    echo ' |  ____|/ __ \ / _|/ _|'
    echo ' | |__  | |  | | |_| |_'
    echo ' |  __| | |  | |  _|  _|'
    echo ' | |    | |__| | | | |'
    echo ' |_|     \____/|_| |_|'
    echo -e "${NC}"
    echo -e "${YELLOW}Fox Operation Manager${NC}"
    echo ""
}

show_help() {
    banner
    echo -e "${CYAN}USAGE:${NC}"
    echo "  ./fox.sh <command> [args]"
    echo "  source fox.sh  (load functions ke shell)"
    echo ""
    echo -e "${CYAN}COMMANDS:${NC}"
    echo ""
    echo -e "  ${GREEN}new${NC} <target> <ip>       Buat operasi baru untuk target"
    echo -e "  ${GREEN}list${NC}                   List semua operasi aktif"
    echo -e "  ${GREEN}open${NC} <target>           Buka file target info"
    echo -e "  ${GREEN}rm${NC} <target>             Hapus operasi (archive dulu)"
    echo -e "  ${GREEN}status${NC} <target>         Lihat status target"
  echo -e "  ${GREEN}note${NC} <target> <text>    Tambah catatan cepat ke target"
  echo -e "  ${GREEN}notes${NC} <target>          Lihat semua catatan target"
  echo -e "  ${GREEN}recon-add${NC} <target>      Tambah hasil recon (interactive)"
    echo ""
    echo -e "  ${GREEN}flow${NC}                    Tampilkan kill chain flow"
    echo -e "  ${GREEN}skills${NC}                  Tampilkan skill matrix"
    echo -e "  ${GREEN}manifest${NC}                Tampilkan fox manifest"
    echo ""
    echo -e "  ${GREEN}help${NC}                    Tampilkan help ini"
    echo ""
    echo -e "${CYAN}EXAMPLES:${NC}"
    echo "  ./fox.sh new example.com 10.10.10.1"
    echo "  ./fox.sh list"
    echo "  ./fox.sh open example.com"
    echo "  ./fox.sh note example.com 'Found SQLi at /products.php?id=1'"
    echo ""
}

# ============================================================
# COMMAND: new — Create new target operation
# ============================================================
cmd_new() {
    local target="$1"
    local ip="$2"

    if [[ -z "$target" || -z "$ip" ]]; then
        echo -e "${RED}Usage: fox new <target> <ip>${NC}"
        return 1
    fi

    local dir="$OPS_DIR/$target"
    if [[ -d "$dir" ]]; then
        echo -e "${YELLOW}[!] Target '$target' already exists!${NC}"
        echo -e "${YELLOW}    Use 'fox open $target' to view it.${NC}"
        return 1
    fi

    mkdir -p "$dir"/{recon,vulns,creds,payloads,loot,exploits}

    # Copy template dan replace placeholder
    cp "$OPS_DIR/template/TARGET.md" "$dir/TARGET.md"
    sed -i "s/\[NAMA TARGET\]/$target/g" "$dir/TARGET.md"
    sed -i "s/example.com/$target/g" "$dir/TARGET.md"
    sed -i "s/10.10.10.1/$ip/g" "$dir/TARGET.md"
    sed -i "s/Date Added    :.*/Date Added    : $(date +%Y-%m-%d)/" "$dir/TARGET.md"

    echo -e "${GREEN}[+] New target created: $target ($ip)${NC}"
    echo -e "${GREEN}    Directory: $dir${NC}"
    echo -e "${GREEN}    Use 'fox open $target' to start working.${NC}"
}

# ============================================================
# COMMAND: list — List all operations
# ============================================================
cmd_list() {
    banner
    echo -e "${CYAN}ACTIVE OPERATIONS:${NC}"
    echo ""

    local found=0
    for dir in "$OPS_DIR"/*/; do
        local name=$(basename "$dir")
        [[ "$name" == "template" ]] && continue
        [[ "$name" == "archive" ]] && continue

        local status="NEW"
        local target_file="$dir/TARGET.md"
        if [[ -f "$target_file" ]]; then
            status=$(grep "^Status" "$target_file" 2>/dev/null | awk -F': ' '{print $2}' | head -1)
        fi

        local ip=$(grep "^IP" "$target_file" 2>/dev/null | awk -F': ' '{print $2}' | head -1)

        echo -e "  ${RED}[${status}]${NC} ${GREEN}$name${NC} ${BLUE}$ip${NC}"
        echo -e "      ${YELLOW}Dir:${NC} $dir"
        echo ""
        found=1
    done

    if [[ $found -eq 0 ]]; then
        echo -e "  ${YELLOW}No active operations.${NC}"
        echo -e "  ${YELLOW}Create one with: fox new <target> <ip>${NC}"
    fi
}

# ============================================================
# COMMAND: open — Open target file
# ============================================================
cmd_open() {
    local target="$1"
    if [[ -z "$target" ]]; then
        echo -e "${RED}Usage: fox open <target>${NC}"
        return 1
    fi

    local target_file="$OPS_DIR/$target/TARGET.md"
    if [[ ! -f "$target_file" ]]; then
        echo -e "${RED}[!] Target '$target' not found!${NC}"
        echo -e "${YELLOW}    Use 'fox list' to see available targets.${NC}"
        echo -e "${YELLOW}    Use 'fox new $target <ip>' to create it.${NC}"
        return 1
    fi

    # Use less to view, or just cat if we're in a simple terminal
    if command -v less &>/dev/null; then
        less "$target_file"
    else
        cat "$target_file"
        echo ""
        echo -e "${CYAN}Target location: $target_file${NC}"
    fi
}

# ============================================================
# COMMAND: rm — Archive operation
# ============================================================
cmd_rm() {
    local target="$1"
    if [[ -z "$target" ]]; then
        echo -e "${RED}Usage: fox rm <target>${NC}"
        return 1
    fi

    local dir="$OPS_DIR/$target"
    if [[ ! -d "$dir" ]]; then
        echo -e "${RED}[!] Target '$target' not found!${NC}"
        return 1
    fi

    local archive_name="${target}_$(date +%Y%m%d_%H%M%S)"
    local archive_dir="$OPS_DIR/archive/$archive_name"

    mkdir -p "$OPS_DIR/archive"
    mv "$dir" "$archive_dir"
    echo -e "${YELLOW}[!] Target '$target' archived to:${NC}"
    echo -e "${YELLOW}    $archive_dir${NC}"
    echo -e "${YELLOW}    Use 'fox list-archived' to see archived targets.${NC}"
}

# ============================================================
# COMMAND: status — Quick status check
# ============================================================
cmd_status() {
    local target="$1"
    if [[ -z "$target" ]]; then
        echo -e "${RED}Usage: fox status <target>${NC}"
        return 1
    fi

    local dir="$OPS_DIR/$target"
    if [[ ! -d "$dir" ]]; then
        echo -e "${RED}[!] Target '$target' not found!${NC}"
        return 1
    fi

    echo -e "${CYAN}===== $target STATUS =====${NC}"

    local target_file="$dir/TARGET.md"
    if [[ -f "$target_file" ]]; then
        head -10 "$target_file" | grep -E "^(Target|IP|Status|Date)"
    fi
    echo ""

    echo -e "${CYAN}Directory Contents:${NC}"
    ls -la "$dir"
    echo ""

    # Count files in subdirectories
    for sub in recon vulns creds payloads loot exploits; do
        local subdir="$dir/$sub"
        if [[ -d "$subdir" ]]; then
            local count=$(find "$subdir" -type f 2>/dev/null | wc -l)
            echo -e "  ${GREEN}$sub:${NC} $count files"
        fi
    done
}

# ============================================================
# COMMAND: note — Add quick note
# ============================================================
cmd_note() {
    local target="$1"
    shift
    local note_text="$*"

    if [[ -z "$target" || -z "$note_text" ]]; then
        echo -e "${RED}Usage: fox note <target> <note text>${NC}"
        return 1
    fi

    local notes_file="$OPS_DIR/$target/notes.log"
    if [[ ! -d "$OPS_DIR/$target" ]]; then
        echo -e "${RED}[!] Target '$target' not found!${NC}"
        return 1
    fi

    echo "[$(date '+%Y-%m-%d %H:%M')] $note_text" >> "$notes_file"
    echo -e "${GREEN}[+] Note added to $target${NC}"

    echo -e "${YELLOW}    View notes: fox notes $target${NC}"
}

# ============================================================
# COMMAND: notes — Show notes log
# ============================================================
cmd_notes() {
    local target="$1"
    if [[ -z "$target" ]]; then
        echo -e "${RED}Usage: fox notes <target>${NC}"
        return 1
    fi

    local notes_file="$OPS_DIR/$target/notes.log"
    if [[ ! -f "$notes_file" ]]; then
        echo -e "${YELLOW}No notes for $target.${NC}"
        return
    fi

    echo -e "${CYAN}===== $target NOTES =====${NC}"
    cat "$notes_file"
}

# ============================================================
# COMMAND: recon-add — Add recon data (interactive prompt)
# ============================================================
cmd_recon_add() {
    local target="$1"
    if [[ -z "$target" ]]; then
        echo -e "${RED}Usage: fox recon-add <target>${NC}"
        return 1
    fi

    local dir="$OPS_DIR/$target"
    if [[ ! -d "$dir" ]]; then
        echo -e "${RED}[!] Target '$target' not found!${NC}"
        return 1
    fi

    echo -e "${CYAN}Add recon data for $target${NC}"
    echo -e "${YELLOW}Enter data (type 'done' to finish):${NC}"

    local recon_file="$dir/recon/recon_data.txt"
    echo "===== RECON DATA — $(date '+%Y-%m-%d %H:%M') =====" >> "$recon_file"
    echo "" >> "$recon_file"

    while true; do
        read -p "> " line
        [[ "$line" == "done" ]] && break
        echo "$line" >> "$recon_file"
    done

    echo "" >> "$recon_file"
    echo -e "${GREEN}[+] Recon data saved to $recon_file${NC}"
}

# ============================================================
# COMMAND: show flow/skills/manifest
# ============================================================
cmd_show() {
    local what="$1"
    local file=""

    case "$what" in
        flow|flow.md)       file="$FOX_HOME/FLOW.md" ;;
        skills|SKILLS.md)   file="$FOX_HOME/SKILLS.md" ;;
        manifest|MANIFEST.md) file="$FOX_HOME/FOX_MANIFEST.md" ;;
        *)
            echo -e "${RED}Available: flow, skills, manifest${NC}"
            return 1
            ;;
    esac

    if [[ -f "$file" ]]; then
        if command -v less &>/dev/null; then
            less "$file"
        else
            cat "$file"
        fi
    else
        echo -e "${RED}[!] File not found: $file${NC}"
    fi
}

# ============================================================
# COMMAND: list-archived — Show archived operations
# ============================================================
cmd_list_archived() {
    local archive_dir="$OPS_DIR/archive"
    if [[ ! -d "$archive_dir" ]]; then
        echo -e "${YELLOW}No archived operations.${NC}"
        return
    fi

    echo -e "${CYAN}ARCHIVED OPERATIONS:${NC}"
    for dir in "$archive_dir"/*/; do
        [[ ! -d "$dir" ]] && continue
        local name=$(basename "$dir")
        echo -e "  ${YELLOW}$name${NC}"
    done
}

# ============================================================
# MAIN
# ============================================================
main() {
    local cmd="$1"
    shift 2>/dev/null

    case "$cmd" in
        new)        cmd_new "$@" ;;
        list)       cmd_list ;;
        open)       cmd_open "$@" ;;
        rm)         cmd_rm "$@" ;;
        status)     cmd_status "$@" ;;
        note)       cmd_note "$@" ;;
        notes)      cmd_notes "$@" ;;
        recon-add)  cmd_recon_add "$@" ;;
        flow|skills|manifest)
                    cmd_show "$cmd" ;;
        list-archived) cmd_list_archived ;;
        help|--help|-h) show_help ;;
        *)
            if [[ -z "$cmd" ]]; then
                show_help
            else
                echo -e "${RED}Unknown command: $cmd${NC}"
                show_help
            fi
            ;;
    esac
}

# If sourced, define 'fox' function instead
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
    fox() {
        main "$@"
    }
    # Also alias f to fox
    alias f='fox'
else
    main "$@"
fi
