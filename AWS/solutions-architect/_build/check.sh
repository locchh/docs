#!/usr/bin/env bash
# Mechanical QA for a course content file.
#
# Usage:
#   bash _build/check.sh services/01-storage/s3.md
#   bash _build/check.sh services/01-storage/s3.md XL   # also checks tier words
#   bash _build/check.sh                                # every content file
#
# Runs from anywhere: paths are resolved against the course root.
# Exit status 0 means no errors. Warnings do not fail the run.
# This script checks what a machine can check. It is not a substitute for the
# review pass described in REVIEW_SPEC.md.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ERRORS=0
WARNINGS=0
TIER=""

err()  { printf '  ERROR   %s\n' "$1"; ERRORS=$((ERRORS + 1)); }
warn() { printf '  warn    %s\n' "$1"; WARNINGS=$((WARNINGS + 1)); }
ok()   { printf '  ok      %s\n' "$1"; }

check_links() {
  # Matches every relative .md link, including same-directory ones like
  # "](ebs.md)". A link whose target does not exist yet but is listed in
  # UNIT_PLAN.md is a warning, not an error, so writers can link units that are
  # planned but not yet written instead of degrading the link to plain text.
  local f="$1" dir="$2" broken=0 pending=0 nlinks=0 target base
  local plan="$ROOT/_build/UNIT_PLAN.md"
  while IFS= read -r target; do
    [[ -z "$target" ]] && continue
    nlinks=$((nlinks + 1))
    [[ -e "$dir/${target%%#*}" ]] && continue
    base="$(basename "${target%%#*}")"
    if [[ -f "$plan" ]] && grep -qF "\`$base\`" "$plan"; then
      pending=$((pending + 1))
    else
      err "broken link, and not a planned file: $target"
      broken=$((broken + 1))
    fi
  done < <(grep -oE '\]\([^):]*\.md[^)]*\)' "$f" \
           | sed 's/^](//; s/)$//' | grep -v '^/' || true)
  [[ "$pending" -gt 0 ]] && warn "$pending link(s) point at planned files not yet written"
  [[ "$broken" -eq 0 && "$nlinks" -gt 0 ]] \
    && ok "$nlinks relative link(s), $((nlinks - pending)) resolve now"
  return 0
}

check_file() {
  local f="$1"
  printf '\n== %s\n' "${f#"$ROOT"/}"

  if [[ ! -f "$f" ]]; then
    err "file does not exist"
    return
  fi

  local dir total body quiz
  dir="$(dirname "$f")"
  total=$(wc -w < "$f")

  # --- banned characters -----------------------------------------------------
  # U+2014 EM DASH is banned. U+2013 EN DASH is allowed (official exam names).
  local emdash
  emdash=$(grep -c '—' "$f" || true)
  if [[ "$emdash" -gt 0 ]]; then
    err "em dash U+2014 appears on $emdash line(s): $(grep -n '—' "$f" | head -3 | cut -d: -f1 | tr '\n' ' ')"
  else
    ok "no em dash"
  fi

  if grep -qP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]' "$f" 2>/dev/null; then
    err "emoji found: line $(grep -nP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]' "$f" | head -1 | cut -d: -f1)"
  fi

  # --- word counts -----------------------------------------------------------
  # Service units end their body at "Knowledge check"; domain guides at "Mixed quiz".
  local quizhead=""
  grep -q '^## Knowledge check' "$f" && quizhead='## Knowledge check'
  grep -q '^## Mixed quiz'      "$f" && quizhead='## Mixed quiz'

  if [[ "$(basename "$f")" == "README.md" ]]; then
    # Index files carry no quiz and no unit template.
    printf '  info    index file, %s words\n' "$total"
    body=0
  elif [[ -n "$quizhead" ]]; then
    body=$(sed "/^${quizhead}/,\$d" "$f" | wc -w)
    printf '  info    body %s words, total %s words' "$body" "$total"
    if [[ -n "$TIER" ]]; then
      local lo hi
      case "$TIER" in
        XL) lo=10000; hi=13000 ;;
        L)  lo=6000;  hi=8000  ;;
        M)  lo=3500;  hi=5000  ;;
        S)  lo=1800;  hi=3000  ;;
        XS) lo=2500;  hi=5000  ;;
        *)  lo=0;     hi=0     ;;
      esac
      if [[ "$hi" -gt 0 ]]; then
        printf ' (tier %s wants %s to %s)' "$TIER" "$lo" "$hi"
        if [[ "$body" -lt "$lo" || "$body" -gt "$hi" ]]; then
          printf '\n'; warn "body word count outside the $TIER range"
        else
          printf '\n'
        fi
      else
        printf '\n'; warn "unknown tier '$TIER', expected XL, L, M, S or XS"
      fi
    else
      printf '\n'
    fi
  else
    err "no '## Knowledge check' (service unit) or '## Mixed quiz' (domain guide) section"
    body=0
  fi

  # --- required sections, in order -------------------------------------------
  local -a required=()
  local kind=""
  if [[ "$f" == *"/services/"* && "$(basename "$f")" != "README.md" ]]; then
    kind="service"
    required=("## Professional depth" "## Worked scenario" "## Exam lens" \
              "## Knowledge check" "## Summary" "## Related units" "## Sources")
  elif [[ "$f" == *"/domains/"* && "$(basename "$f")" != "README.md" ]]; then
    kind="domain"
    required=("## Decision tables" "## Words that give the answer away" \
              "## The domain on one page" "## Mixed quiz" "## Where to read more")
  fi

  if [[ -n "$kind" ]]; then
    local prev=0 missing=0
    for sec in "${required[@]}"; do
      local line
      line=$(grep -n "^${sec}\$" "$f" | head -1 | cut -d: -f1)
      if [[ -z "$line" ]]; then
        err "missing section: $sec"
        missing=1
      elif [[ "$line" -lt "$prev" ]]; then
        err "section out of order: $sec"
      else
        prev="$line"
      fi
    done
    [[ "$missing" -eq 0 ]] && ok "all required sections present and ordered"

    # Opening lead paragraph
    if [[ "$kind" == "service" ]]; then
      grep -q '^\*\*Where it sits on the exams\.\*\*' "$f" \
        || err "missing '**Where it sits on the exams.**' lead paragraph"
    else
      grep -q '^\*\*Weight and shape\.\*\*' "$f" \
        || err "missing '**Weight and shape.**' lead paragraph"
    fi

    # Exactly one H1
    local h1
    h1=$(grep -c '^# ' "$f" || true)
    [[ "$h1" -eq 1 ]] || err "expected exactly 1 H1, found $h1"
  fi

  # --- quiz ------------------------------------------------------------------
  if [[ "$(basename "$f")" == "README.md" ]]; then
    check_links "$f" "$dir"
    return
  fi

  quiz=$(grep -c '^### [0-9]\+\.' "$f" || true)
  local details close answers
  details=$(grep -c '<details><summary>Answer</summary>' "$f" || true)
  close=$(grep -c '^</details>' "$f" || true)
  answers=$(grep -c '^\*\*Answer: ' "$f" || true)

  printf '  info    quiz %s questions, %s answer folds\n' "$quiz" "$details"

  [[ "$details" -eq "$close" ]] || err "unbalanced answer folds: $details open, $close close"
  [[ "$details" -eq "$answers" ]] || err "$details folds but $answers '**Answer:' lines"
  [[ "$quiz" -eq "$details" ]] || err "$quiz numbered questions but $details answer folds"

  if [[ "$quiz" -gt 0 ]]; then
    local labeled
    labeled=$(grep -c '^### [0-9]\+\..*(\(Associate\|Professional\))$' "$f" || true)
    [[ "$labeled" -eq "$quiz" ]] \
      || err "$quiz questions but $labeled carry an (Associate) or (Professional) label"

    local where
    where=$(grep -c '^\*Where this is covered: ' "$f" || true)
    [[ "$where" -eq "$quiz" ]] \
      || err "$quiz questions but $where 'Where this is covered' lines"

    # Every "Where this is covered" target must be a real ## section in this file
    while IFS= read -r target; do
      [[ -z "$target" ]] && continue
      grep -qF "## $target" "$f" \
        || err "'Where this is covered: $target' does not match any section heading"
    done < <(grep '^\*Where this is covered: ' "$f" \
             | sed 's/^\*Where this is covered: //; s/\.\*$//' || true)

    local mr
    mr=$(grep -c 'Select \(TWO\|THREE\)\.' "$f" || true)
    if [[ "$mr" -eq 0 ]]; then
      warn "no multiple response questions; spec asks for at least a quarter"
    else
      printf '  info    %s multiple response question(s)\n' "$mr"
    fi

    # Count only the key letters themselves. The rationale shares the line, so
    # anchoring on the letter position matters: a pattern with .* before the
    # letter counts every Amazon, AWS, EC2 and ECS in the prose.
    #
    # Report multiple-choice keys separately. Aggregating them with
    # multiple-response letters hides clustering: a unit whose four single-answer
    # keys are all B and C can still show a flat A-to-E spread.
    local keys mc
    keys=$(grep -oE '^\*\*Answer: [A-E]( and [A-E])*' "$f" | sed 's/^\*\*Answer: //')
    printf '  info    key spread, all: %s\n' \
      "$(grep -oE '[A-E]' <<<"$keys" | sort | uniq -c | awk '{printf "%s=%s ", $2, $1}')"
    mc=$(grep -v ' and ' <<<"$keys")
    if [[ -n "$mc" ]]; then
      printf '  info    key spread, multiple choice only: %s\n' \
        "$(grep -oE '[A-E]' <<<"$mc" | sort | uniq -c | awk '{printf "%s=%s ", $2, $1}')"
      local distinct total_mc
      distinct=$(grep -oE '[A-E]' <<<"$mc" | sort -u | wc -l)
      total_mc=$(grep -c . <<<"$mc")
      [[ "$total_mc" -ge 4 && "$distinct" -lt 3 ]] \
        && warn "multiple choice keys use only $distinct distinct letters across $total_mc questions"
    fi
  fi

  # --- links -----------------------------------------------------------------
  check_links "$f" "$dir"

  # --- quiz stem register ----------------------------------------------------
  # STYLE_SPEC fixes the five endings a scenario may close with. A stem that
  # drifts reads as a different exam and is invisible to every other check.
  if grep -q '^## Knowledge check' "$f"; then
    local nq nstem
    nq=$(grep -c '^### [0-9]' "$f" || true)
    nstem=$(grep -cE '^Which (solution|combination of steps) will meet these requirements( MOST cost-effectively| with the LEAST (operational overhead|latency))?\?( \(Select (TWO|THREE)\.\))?$' "$f" || true)
    if [[ "$nstem" -eq "$nq" ]]; then
      ok "all $nq quiz stem(s) use an approved ending"
    else
      err "$((nq - nstem)) of $nq quiz stem(s) do not end with an approved question, see STYLE_SPEC"
    fi
  fi

  # --- sources ---------------------------------------------------------------
  if grep -q '^## Sources' "$f"; then
    local bad
    bad=$(sed -n '/^## Sources/,$p' "$f" \
          | grep -o 'https\?://[^) ]*' \
          | grep -v -E '^https://(docs\.aws\.amazon\.com|aws\.amazon\.com)' \
          | sort -u || true)
    if [[ -n "$bad" ]]; then
      err "non-AWS source(s): $(echo "$bad" | tr '\n' ' ')"
    else
      ok "sources all on AWS hosts"
    fi
    local nsrc
    nsrc=$(sed -n '/^## Sources/,$p' "$f" | grep -c '^- \[' || true)
    printf '  info    %s source(s)\n' "$nsrc"
    [[ "$nsrc" -lt 8 ]] && warn "fewer than 8 sources"

    # Retired AWS doc pages still return 200: they redirect to the guide root.
    # A URL whose effective address ends in / lost its page. Opt-in because it
    # needs the network. Run: CHECK_URLS=1 bash check.sh <file> <TIER>
    if [[ -n "${CHECK_URLS:-}" ]]; then
      local dead=0 u eff
      while read -r u; do
        [[ -z "$u" ]] && continue
        eff=$(curl -sL -o /dev/null -w '%{url_effective}' --max-time 20 "$u" 2>/dev/null || true)
        # Dead only when the page redirected UP to an ancestor of itself.
        # A URL that legitimately ends in / (a pricing page) is left alone.
        if [[ -z "$eff" || ( "$eff" != "$u" && "$u" == "$eff"* ) ]]; then
          err "source URL no longer resolves to a page: $u"
          dead=$((dead + 1))
        fi
      done < <(sed -n '/^## Sources/,$p' "$f" | grep -o 'https\?://[^) ]*' | sort -u)
      [[ "$dead" -eq 0 ]] && ok "all source URLs resolve to a real page"
    fi
  fi
}

main() {
  # A bare tier token as the last argument applies to the files named before it.
  if [[ $# -gt 1 && "${!#}" =~ ^(XL|L|M|S|XS)$ ]]; then
    TIER="${!#}"
    set -- "${@:1:$(($# - 1))}"
  fi

  if [[ $# -gt 0 ]]; then
    for arg in "$@"; do
      [[ "$arg" = /* ]] && check_file "$arg" || check_file "$ROOT/${arg#aws/solutions-architect/}"
    done
  else
    while IFS= read -r f; do check_file "$f"; done < <(
      find "$ROOT/services" "$ROOT/domains" "$ROOT/appendix" -name '*.md' 2>/dev/null | sort
    )
  fi

  printf '\n-- %s error(s), %s warning(s)\n' "$ERRORS" "$WARNINGS"
  [[ "$ERRORS" -eq 0 ]]
}

main "$@"
