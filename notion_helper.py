#!/usr/bin/env python3
"""
Notion Helper - Dynamic property detection and utilities for Notion integration

This module provides utilities to work with Notion databases that have
different property names and schemas, avoiding hardcoded property names.
"""

import os
from typing import Optional, Dict, Any
from notion_client import Client
from functools import lru_cache


class NotionDatabaseHelper:
    """Helper class for working with Notion databases dynamically"""

    def __init__(self, api_key: str = None, database_id: str = None):
        """
        Initialize the helper.

        Args:
            api_key: Notion API key (or from NOTION_API_KEY env var)
            database_id: Notion database ID (or from NOTION_DATABASE_ID env var)
        """
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")

        if not self.api_key or not self.database_id:
            raise ValueError("NOTION_API_KEY and NOTION_DATABASE_ID must be set")

        self.notion = Client(auth=self.api_key)
        self._property_cache: Dict[str, str] = {}

    def get_database_schema(self) -> Dict[str, Any]:
        """
        Get the database schema/properties.

        Returns:
            Dictionary of property configurations
        """
        try:
            database = self.notion.databases.retrieve(self.database_id)
            return database.get("properties", {})
        except Exception as e:
            print(f"[Warning] Could not retrieve database schema: {e}")
            return {}

    @lru_cache(maxsize=1)
    def find_title_property(self) -> str:
        """
        Find the title property name in the database.

        Returns:
            Property name (e.g., "Title", "Name", "title")

        Note: Results are cached to avoid repeated API calls.
        """
        schema = self.get_database_schema()

        # Look for title type property
        for prop_name, prop_data in schema.items():
            if prop_data.get("type") == "title":
                print(f"[Notion] Detected title property: '{prop_name}'")
                self._property_cache['title'] = prop_name
                return prop_name

        # Fallback to common names
        fallback_names = ["Title", "Name", "title", "name"]
        for name in fallback_names:
            if name in schema:
                print(f"[Notion] Using fallback title property: '{name}'")
                self._property_cache['title'] = name
                return name

        print("[Notion] No title property found, using 'Title'")
        self._property_cache['title'] = "Title"
        return "Title"

    @lru_cache(maxsize=1)
    def find_status_property(self) -> Optional[str]:
        """
        Find the status property name and type in the database.

        Returns:
            Property name or None if not found

        Note: Results are cached to avoid repeated API calls.
        """
        schema = self.get_database_schema()

        # Look for status or select type property
        for prop_name, prop_data in schema.items():
            prop_type = prop_data.get("type")
            if prop_type in ["status", "select"]:
                print(f"[Notion] Detected status property: '{prop_name}' (type: {prop_type})")
                self._property_cache['status'] = prop_name
                self._property_cache['status_type'] = prop_type
                return prop_name

        # Fallback to common names
        fallback_names = ["Status", "status", "State", "state"]
        for name in fallback_names:
            if name in schema:
                prop_type = schema[name].get("type")
                print(f"[Notion] Using fallback status property: '{name}' (type: {prop_type})")
                self._property_cache['status'] = name
                self._property_cache['status_type'] = prop_type
                return name

        print("[Notion] No status property found")
        self._property_cache['status'] = None
        return None

    def get_status_property_type(self) -> Optional[str]:
        """
        Get the type of the status property (status or select).

        Returns:
            'status', 'select', or None
        """
        if 'status_type' in self._property_cache:
            return self._property_cache['status_type']

        self.find_status_property()  # Populates the cache
        return self._property_cache.get('status_type')

    def find_content_property(self) -> Optional[str]:
        """
        Find a property suitable for storing content (text type).

        Returns:
            Property name or None if not found
        """
        schema = self.get_database_schema()

        # Look for rich_text or text type property
        for prop_name, prop_data in schema.items():
            prop_type = prop_data.get("type")
            if prop_type in ["rich_text", "text"]:
                if prop_name.lower() in ["content", "text", "description", "body"]:
                    print(f"[Notion] Detected content property: '{prop_name}'")
                    return prop_name

        # Fallback
        fallback_names = ["Content", "Text", "content", "text"]
        for name in fallback_names:
            if name in schema:
                print(f"[Notion] Using fallback content property: '{name}'")
                return name

        print("[Notion] No content property found")
        return None

    def build_page_properties(self, title: str, status: str = "Draft",
                              content: str = None, **extra_props) -> Dict[str, Any]:
        """
        Build page properties dictionary with correct property names and types.

        Args:
            title: Page title
            status: Status value (default: "Draft")
            content: Optional content text
            **extra_props: Additional properties (e.g., Type="Personal")

        Returns:
            Properties dictionary ready for notion.pages.create()
        """
        properties = {}

        # Title property
        title_prop = self.find_title_property()
        properties[title_prop] = {
            "title": [{"text": {"content": title}}]
        }

        # Status property
        status_prop = self.find_status_property()
        if status_prop:
            status_type = self.get_status_property_type()
            if status_type == "status":
                properties[status_prop] = {"status": {"name": status}}
            elif status_type == "select":
                properties[status_prop] = {"select": {"name": status}}

        # Content property (if provided)
        if content:
            content_prop = self.find_content_property()
            if content_prop:
                schema = self.get_database_schema()
                prop_type = schema[content_prop].get("type")
                if prop_type == "rich_text":
                    properties[content_prop] = {
                        prop_type: [{"text": {"content": content}}]
                    }
                elif prop_type == "text":
                    properties[content_prop] = {
                        prop_type: {"content": content}
                    }

        # Extra properties
        for key, value in extra_props.items():
            # Check if property exists
            schema = self.get_database_schema()
            if key in schema:
                prop_type = schema[key].get("type")
                if prop_type == "select":
                    properties[key] = {"select": {"name": value}}
                elif prop_type == "rich_text":
                    properties[key] = {prop_type: [{"text": {"content": str(value)}}]}
                elif prop_type == "text":
                    properties[key] = {prop_type: {"content": str(value)}}

        return properties

    def update_page_status(self, page_id: str, status: str) -> bool:
        """
        Update the status of a page.

        Args:
            page_id: Notion page ID
            status: New status value

        Returns:
            True if successful, False otherwise
        """
        status_prop = self.find_status_property()
        if not status_prop:
            print(f"[Warning] No status property found, cannot update status")
            return False

        status_type = self.get_status_property_type()

        try:
            if status_type == "status":
                self.notion.pages.update(
                    page_id=page_id,
                    properties={status_prop: {"status": {"name": status}}}
                )
            elif status_type == "select":
                self.notion.pages.update(
                    page_id=page_id,
                    properties={status_prop: {"select": {"name": status}}}
                )
            return True
        except Exception as e:
            print(f"[Error] Failed to update status: {e}")
            return False

    def clear_cache(self):
        """Clear the property cache (useful if database schema changes)"""
        self.find_title_property.cache_clear()
        self.find_status_property.cache_clear()
        self._property_cache.clear()


# Convenience functions for backward compatibility
def get_notion_helper(api_key: str = None, database_id: str = None) -> NotionDatabaseHelper:
    """Get a NotionDatabaseHelper instance."""
    return NotionDatabaseHelper(api_key, database_id)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    # Test the helper
    print("=" * 70)
    print("NOTION DATABASE HELPER TEST")
    print("=" * 70)
    print()

    try:
        helper = get_notion_helper()

        print("Detected Properties:")
        print(f"  Title: {helper.find_title_property()}")
        print(f"  Status: {helper.find_status_property()} (type: {helper.get_status_property_type()})")
        print(f"  Content: {helper.find_content_property()}")
        print()

        # Test building properties
        props = helper.build_page_properties(
            title="Test Post",
            status="Draft",
            Type="Personal"
        )
        print("Built properties:")
        for key, value in props.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"Error: {e}")
