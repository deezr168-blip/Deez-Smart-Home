#!/bin/sh
# CasaRay recovery CR-REC-25 -- READ-ONLY evidence pass, v1.3 candidate (30/10/2026).
# v1.3: rd() also requires a symlink's resolved target to be allowlisted (v1.2 only denylisted it).
# Run in the Terminal & SSH add-on:   sh /tmp/casaray_evidence.sh
#
# Reads ONLY the files named in ALLOW below, and every read goes through rd(),
# which enforces that allowlist plus a denylist. Prints dashboard registrations,
# yes/no presence indicators, theme presence, SHA-256 hashes of the dashboard and
# theme files, and dependency folder names.
# Never: writes, deletes, restarts, reloads, calls Home Assistant or the
# Supervisor, reads logs, prints backup slugs, or opens secrets.yaml,
# .storage/auth*, .cloud/, esphome/, .deez_deploy.env or the login-recovery
# copies under _recovery/.

H_DASH=77a4991626d6f8afcd9b78f235c34417d84d9f36c129549a386d8a66c324226c
H_LEGACY=e02124b56322f69d87c837b008bb4f6c84bb3fc2892ea93c446c12b98dd17dc1
H_THEME=ef7dc9fb2445a6baa2f597fc143927b6da2a60142aef2d0f76dc211f79fdb614

C=""
for d in /config /homeassistant; do
  if [ -f "$d/configuration.yaml" ]; then C=$d; break; fi
done
[ -n "$C" ] || { echo "config folder not found"; exit 1; }
CR=$(readlink -f "$C")
S="$C/.storage"

# The only files this script may open, relative to the config folder.
ALLOW='configuration.yaml
input_boolean.yaml
input_number.yaml
input_select.yaml
input_text.yaml
input_datetime.yaml
person.yaml
people.yaml
helpers.yaml
dashboards/casaray_v2.yaml
dashboards/deez_smart_home.yaml
themes/deez_your_name.yaml
deez_repo/dashboards/casaray_v2.yaml
deez_repo/themes/deez_your_name.yaml
_recovery/casaray/configuration.yaml.pre
.storage/lovelace_dashboards
.storage/lovelace_resources
.storage/repairs.issue_registry
.storage/person
.storage/input_boolean
.storage/input_number
.storage/input_select
.storage/input_text
.storage/input_datetime'

DENY() {
  case "$1" in
    *secret*|*auth*|*cloud*|*esphome*|*deploy*|*askpass*|*token*|*credential*|*password*|*.env|*.key|*.pem) return 0 ;;
    *_recovery/owner*|*_recovery/stage*|*_recovery/pre/*|*_recovery/rolledback*) return 0 ;;
  esac
  return 1
}

# rd <path relative to the config folder>: print the file, or nothing if it is
# not allowlisted, is denylisted, resolves outside the config folder, or is not
# a regular file. Symlinks are resolved first, and the target must itself be
# allowlisted and not denylisted.
rd() {
  DENY "$1" && return 1
  printf '%s\n' "$ALLOW" | grep -qxF "$1" || return 1
  r=$(readlink -f "$C/$1" 2>/dev/null) || return 1
  case "$r" in "$CR"/*) ;; *) return 1 ;; esac
  DENY "${r#"$CR"/}" && return 1
  printf '%s\n' "$ALLOW" | grep -qxF "${r#"$CR"/}" || return 1
  [ -f "$r" ] || return 1
  cat "$r"
}

h() { echo; echo "== $*"; }
line() { printf '  %-40s %s\n' "$1" "$2"; }
orn() { awk '{ print; n++ } END { if (!n) print "    none" }'; }
names() { for p in "$1"/*; do [ -e "$p" ] && echo "    ${p##*/}"; done | orn; }
has() { printf '%s\n' "$2" | grep -qE "$1" && echo yes || echo no; }
meta() {
  if [ -d "$C/$1" ]; then
    stat -c '%y' "$C/$1" | sed -E 's/^([0-9-]+ [0-9]{2}:[0-9]{2})[^ ]* ?([-+][0-9]{4})?.*/present (folder)  \1 \2/'
  elif [ -e "$C/$1" ]; then
    stat -c '%y|%s' "$C/$1" | sed -E 's/^([0-9-]+ [0-9]{2}:[0-9]{2})[^ |]* ?([-+][0-9]{4})?[|](.*)$/present  \1 \2  \3 bytes/'
  else
    echo MISSING
  fi
}

echo "CasaRay evidence v1.3 (read-only)   config folder: $C"

h "1 configuration.yaml"
line "file" "$(meta configuration.yaml)"
CFG=$(rd configuration.yaml)
if [ -z "$CFG" ]; then
  line "readable and non-empty" "no"
else
  extra=$(printf '%s\n' "$CFG" | grep -oE '^[a-z_]+:' | tr -d ':' \
    | grep -vxE 'default_config|frontend|automation|script|scene' | grep -c .)
  if [ "$extra" -eq 0 ]; then dflt=yes; else dflt="no ($extra other top-level keys)"; fi
  line "only the generated default keys" "$dflt"
  line "top-level lovelace:" "$(has '^lovelace:' "$CFG")"
  line "top-level homeassistant:" "$(has '^homeassistant:' "$CFG")"
  line "registers casaray-v2" "$(has '^[[:space:]]+casaray-v2:' "$CFG")"
  line "loads packages/" "$(has '^[[:space:]]*packages:[[:space:]]*!include' "$CFG")"
  line "loads the themes/ folder" "$(has '^[[:space:]]*themes:[[:space:]]*!include_dir_merge_named[[:space:]]+themes' "$CFG")"
  line "frontend extra_module_url" "$(has 'extra_module_url' "$CFG")"
fi

h "2 dashboard registrations (.storage)"
line "lovelace_dashboards" "$(meta .storage/lovelace_dashboards)"
echo "  UI dashboards registered (url_path, mode):"
rd .storage/lovelace_dashboards | grep -oE '"(id|url_path|mode)": *"[^"]*"' \
  | sed -E 's/^"([a-z_]+)": *"([^"]*)"$/\1 \2/' \
  | awk '$1 == "id" { if (n) printf "    %-30s %s\n", u, m; n = 1; u = "?"; m = "?"; next }
         $1 == "url_path" { u = $2 }
         $1 == "mode" { m = $2 }
         END { if (n) printf "    %-30s %s\n", u, m; else print "    none" }'
echo "  dashboard content files (not read):"
for p in "$S/lovelace" "$S"/lovelace.*; do
  f=${p##*/}
  case "$f" in *.corrupt.*) continue ;; esac
  [ -e "$p" ] && printf '    %-36s %s\n' "$f" "$(meta ".storage/$f")"
done | orn
line "legacy content lovelace.deez_smart_home" "$(meta .storage/lovelace.deez_smart_home)"
echo "  corrupt dashboard-file copies:"
for p in "$S"/lovelace*.corrupt.*; do [ -e "$p" ] && echo "    ${p##*/}"; done | orn
echo "  dashboard-related repairs:"
rd .storage/repairs.issue_registry | grep -oE '"issue_id": *"[^"]*"' \
  | sed -E 's/^"issue_id": *"//; s/"$//' | grep -E 'lovelace|yaml_mode_deprecated' | sed 's/^/    /' | orn

h "3 frontend resources (dependency names only)"
line "lovelace_resources" "$(meta .storage/lovelace_resources)"
rd .storage/lovelace_resources | grep -oE '"url": *"[^"]*"' \
  | sed -E 's/^"url": *"//; s/"$//; s/[?#].*$//; s#^[A-Za-z][A-Za-z0-9+.-]*://[^/]*##; s#^.*/([^/]+/[^/]+)$#\1#; s#^/##; s/^/    /' | orn

h "4 CasaRay dashboard and theme files"
line "dashboards/ folder" "$(meta dashboards)"
line "themes/ folder" "$(meta themes)"
echo "  theme files present (names):"
names "$C/themes"
for p in "dashboards/casaray_v2.yaml $H_DASH" "dashboards/deez_smart_home.yaml $H_LEGACY" \
         "themes/deez_your_name.yaml $H_THEME" "deez_repo/dashboards/casaray_v2.yaml $H_DASH" \
         "deez_repo/themes/deez_your_name.yaml $H_THEME"; do
  f=${p% *}; want=${p#* }
  line "$f" "$(meta "$f")"
  if [ -e "$C/$f" ]; then
    if rd "$f" >/dev/null 2>&1; then
      got=$(rd "$f" | sha256sum | cut -d' ' -f1)
      if [ "$got" = "$want" ]; then v="MATCHES git"; else v="DIFFERS from git"; fi
      echo "      sha256 $got  $v"
    else
      echo "      not read (refused: symlink outside the config folder or not a regular file)"
    fi
  fi
done
line "/casaray-v2/ links in live dashboard" "$(rd dashboards/casaray_v2.yaml | grep -c '/casaray-v2/')"
line "www/your_name_night_sky.jpg (legacy)" "$(meta www/your_name_night_sky.jpg)"

h "5 helpers and people CasaRay needs (where defined)"
YAML_SRC='configuration.yaml input_boolean.yaml input_number.yaml input_select.yaml input_text.yaml input_datetime.yaml person.yaml people.yaml helpers.yaml'
STORE_SRC='.storage/input_boolean .storage/input_number .storage/input_select .storage/input_text .storage/input_datetime .storage/person'
for k in chinese_dashboard family_location gas_bill_mj raymond_du; do
  y=""; for f in $YAML_SRC; do
    rd "$f" | grep -qE "^[[:space:]]*$k:|id:[[:space:]]*$k([^a-z0-9_]|\$)" && y="$y $f"
  done
  s=""; for f in $STORE_SRC; do
    rd "$f" | grep -q "\"$k\"" && s="$s ${f#.storage/}"
  done
  printf '  %-18s yaml:%s   storage:%s\n' "$k" "${y:- none}" "${s:- none}"
done
echo "  root-level helper files present:"
for f in input_boolean.yaml input_number.yaml input_select.yaml input_text.yaml input_datetime.yaml person.yaml people.yaml helpers.yaml; do
  [ -f "$C/$f" ] && echo "    $f"
done | orn
line "packages/ folder" "$(meta packages)"
echo "  package files (names only, not read):"
names "$C/packages"

h "6 the 30/09 CasaRay registration attempt (presence only)"
line "_recovery/casaray/ folder" "$(meta _recovery/casaray)"
line "configuration.yaml.pre" "$(meta _recovery/casaray/configuration.yaml.pre)"
PRE=$(rd _recovery/casaray/configuration.yaml.pre)
if [ -n "$PRE" ]; then
  line "  pre-copy registers casaray-v2" "$(has '^[[:space:]]+casaray-v2:' "$PRE")"
  line "  pre-copy has top-level lovelace:" "$(has '^lovelace:' "$PRE")"
fi
line "APPLIED marker" "$(meta _recovery/casaray/APPLIED)"
if [ -e "$C/_recovery/casaray/backup_slug" ]; then b="present (content not read)"; else b=MISSING; fi
line "backup reference file" "$b"

h "7 frontend and integration dependencies (folder names only)"
echo "  custom_components/:"
names "$C/custom_components"
echo "  www/community/:"
names "$C/www/community"

echo
echo "== END (read-only; nothing was changed)"
