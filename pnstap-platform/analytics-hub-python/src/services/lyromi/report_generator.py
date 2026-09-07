from .ollama import Ollama


class ReportGenerator:

    @staticmethod
    def generate(data):

        prompt = f"""
You are LYROMI,
Enterprise Chief AI Security Analyst.

Generate a professional executive security report.

Enterprise Data (JSON):

{repr(data)}

The report must contain:

# Executive Security Report

## Executive Summary

## Organization Health

## Threat Analysis

## Infrastructure Status

## Risk Assessment

## Recommendations

Do not invent data.

If data is missing,
say "No data available."

Write professionally.
"""

        return Ollama.ask(
            system_prompt=prompt,
            message="Generate report",
            history=[]
        )
