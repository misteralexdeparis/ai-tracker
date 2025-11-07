#!/usr/bin/env python3
import json
import os
from datetime import datetime

def validate_gartner_rules(tools):
    violations = []
    
    for tool in tools:
        v = tool.get("vision", 0)
        a = tool.get("ability", 0)
        q = tool.get("quadrant", "")
        
        if q == "Visionary" and a >= 50:
            violations.append(f"ERROR: {tool['name']}: Visionary but Ability={a} (must be <50)")
        
        if q == "Challenger" and v >= 50:
            violations.append(f"ERROR: {tool['name']}: Challenger but Vision={v} (must be <50)")
        
        if not (0 <= v <= 100):
            violations.append(f"ERROR: {tool['name']}: Vision={v} (out of bounds 0-100)")
        
        if not (0 <= a <= 100):
            violations.append(f"ERROR: {tool['name']}: Ability={a} (out of bounds 0-100)")
    
    return violations

def main():
    print("AI Tracker - Pipeline Validation")
    print("=" * 60)
    
    json_file = "public/ai_tracker_enhanced.json"
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            tools = json.load(f)
        
        print(f"OK JSON loaded: {len(tools)} tools")
        
        violations = validate_gartner_rules(tools)
        
        if violations:
            print("\nViolations found:")
            for v in violations:
                print(v)
            exit(1)
        else:
            print("OK All Gartner rules validated!")
        
        leaders = len([t for t in tools if t.get("quadrant") == "Leader"])
        visionaries = len([t for t in tools if t.get("quadrant") == "Visionary"])
        challengers = len([t for t in tools if t.get("quadrant") == "Challenger"])
        niche = len([t for t in tools if t.get("quadrant") == "Niche"])
        
        print("\nDistribution:")
        print(f"   Leaders: {leaders}")
        print(f"   Visionaries: {visionaries}")
        print(f"   Challengers: {challengers}")
        print(f"   Niche: {niche}")
        print(f"   TOTAL: {len(tools)}")
        
        print("\nOK Pipeline completed successfully!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)

if __name__ == "__main__":
    main()
