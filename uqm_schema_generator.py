#!/usr/bin/env python3
"""
UQM JSON Schema Generator with OpenRouter Integration

This script:
1. Reads query cases from 查询用例.md
2. Uses OpenRouter API to generate UQM JSON schemas
3. Calls the UQM execution API
4. Saves results to jsonResult folder
"""

import os
import json
import re
import requests
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UQMSchemaGenerator:
    def __init__(self, openrouter_api_key: str, uqm_api_base: str = "http://localhost:8000", 
                 model: str = "anthropic/claude-3.5-sonnet"):
        """
        Initialize the UQM Schema Generator
        
        Args:
            openrouter_api_key: OpenRouter API key
            uqm_api_base: Base URL for UQM API
            model: OpenRouter model to use
        """
        self.openrouter_api_key = openrouter_api_key
        self.uqm_api_base = uqm_api_base
        self.model = model
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        # Create output directory
        self.output_dir = "jsonResult"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # Load guide and schema docs
        self.guide_content = self._load_file("UQM_AI_Assistant_Guide.md")
        self.schema_content = self._load_file("数据库表结构简化描述.md")
        
    def _load_file(self, filename: str) -> str:
        """Load content from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"File {filename} not found")
            return ""
    
    def extract_queries_from_file(self, filename: str = "查询用例.md") -> List[Dict[str, Any]]:
        """
        Extract individual query cases from the markdown file
        
        Returns:
            List of query dictionaries with id, title, and description
        """
        content = self._load_file(filename)
        if not content:
            return []
            
        queries = []
        
        # Regular expression to match numbered items
        pattern = r'(\d+)\.\s+(.+?)(?=\n\s*\d+\.|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            query_id = int(match[0])
            query_text = match[1].strip()
            
            # Clean up the query text
            query_text = re.sub(r'\s+', ' ', query_text)
            
            queries.append({
                "id": query_id,
                "title": query_text[:100] + "..." if len(query_text) > 100 else query_text,
                "description": query_text
            })
            
        logger.info(f"Extracted {len(queries)} queries from {filename}")
        return queries
    
    def generate_uqm_schema(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Use OpenRouter to generate UQM JSON schema for a query
        
        Args:
            query: Query dictionary with id, title, description
            
        Returns:
            Generated UQM JSON schema or None if failed
        """
        
        prompt = f"""
作为UQM专家，请根据以下信息生成标准的UQM JSON配置：

数据库表结构：
{self.schema_content}

UQM指南：
{self.guide_content}

查询需求：
{query['description']}

请严格按照UQM_AI_Assistant_Guide.md中的JSON格式要求生成完整的API调用结构，包含：
1. uqm字段（包含metadata、steps、output）
2. parameters字段（动态参数）
3. options字段（执行选项）

注意：
- 必须使用calculated_fields进行聚合计算
- 聚合查询需要配合group_by使用
- 字段引用格式：表名.字段名
- 参数化使用${{参数名}}格式
- 返回纯JSON格式，不要包含任何解释文字

"""

        try:
            response = requests.post(
                f"{self.openrouter_base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 4000
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Extract JSON from the response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        schema = json.loads(json_match.group())
                        logger.info(f"Generated schema for query {query['id']}")
                        return schema
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON for query {query['id']}: {e}")
                        return None
                else:
                    logger.error(f"No JSON found in response for query {query['id']}")
                    return None
            else:
                logger.error(f"OpenRouter API error for query {query['id']}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating schema for query {query['id']}: {e}")
            return None
    
    def execute_uqm_query(self, schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute UQM query via API
        
        Args:
            schema: UQM JSON schema
            
        Returns:
            API response or None if failed
        """
        try:
            response = requests.post(
                f"{self.uqm_api_base}/api/v1/execute",
                json=schema,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"UQM API error: {response.status_code} - {response.text}")
                return {
                    "error": f"API Error {response.status_code}",
                    "message": response.text
                }
                
        except Exception as e:
            logger.error(f"Error executing UQM query: {e}")
            return {
                "error": "Execution Error",
                "message": str(e)
            }
    
    def save_result(self, query: Dict[str, Any], schema: Dict[str, Any], 
                   execution_result: Dict[str, Any]) -> str:
        """
        Save query, schema, and execution result to JSON file
        
        Args:
            query: Original query
            schema: Generated UQM schema
            execution_result: API execution result
            
        Returns:
            Filename of saved result
        """
        result = {
            "query": {
                "id": query["id"],
                "title": query["title"],
                "description": query["description"]
            },
            "generated_schema": schema,
            "execution_result": execution_result,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator_version": "1.0"
            }
        }
        
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', query["title"])
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        filename = f"query_{query['id']:03d}_{safe_title[:50]}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved result to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving result: {e}")
            return ""
    
    def process_all_queries(self, limit: Optional[int] = None, 
                          start_from: int = 1) -> List[str]:
        """
        Process all queries from the file
        
        Args:
            limit: Maximum number of queries to process
            start_from: Query ID to start from
            
        Returns:
            List of generated filenames
        """
        queries = self.extract_queries_from_file()
        if not queries:
            logger.error("No queries found to process")
            return []
        
        # Filter queries
        filtered_queries = [q for q in queries if q["id"] >= start_from]
        if limit:
            filtered_queries = filtered_queries[:limit]
            
        logger.info(f"Processing {len(filtered_queries)} queries (starting from {start_from})")
        
        generated_files = []
        
        for i, query in enumerate(filtered_queries):
            logger.info(f"Processing query {query['id']}/{len(queries)}: {query['title'][:50]}...")
            
            # Generate schema
            schema = self.generate_uqm_schema(query)
            if not schema:
                logger.warning(f"Skipping query {query['id']} - schema generation failed")
                continue
            
            # Execute query
            execution_result = self.execute_uqm_query(schema)
            if not execution_result:
                logger.warning(f"Query {query['id']} execution failed")
                execution_result = {"error": "Execution failed"}
            
            # Save result
            filename = self.save_result(query, schema, execution_result)
            if filename:
                generated_files.append(filename)
            
            # Rate limiting - wait between requests
            if i < len(filtered_queries) - 1:
                time.sleep(2)
                
        logger.info(f"Completed processing. Generated {len(generated_files)} files.")
        return generated_files
    
    def process_single_query(self, query_id: int) -> Optional[str]:
        """
        Process a single query by ID
        
        Args:
            query_id: ID of query to process
            
        Returns:
            Generated filename or None if failed
        """
        queries = self.extract_queries_from_file()
        query = next((q for q in queries if q["id"] == query_id), None)
        
        if not query:
            logger.error(f"Query {query_id} not found")
            return None
            
        logger.info(f"Processing single query {query_id}: {query['title'][:50]}...")
        
        # Generate schema
        schema = self.generate_uqm_schema(query)
        if not schema:
            logger.error(f"Schema generation failed for query {query_id}")
            return None
        
        # Execute query
        execution_result = self.execute_uqm_query(schema)
        if not execution_result:
            execution_result = {"error": "Execution failed"}
        
        # Save result
        return self.save_result(query, schema, execution_result)


def main():
    """Main function to run the UQM Schema Generator"""
    
    # Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or "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"
    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY environment variable not set")
        print("Please set it with: $env:OPENROUTER_API_KEY='your_api_key'")
        return
    
    UQM_API_BASE = os.getenv("UQM_API_BASE", "http://localhost:8000")
    
    # Model configuration - change this to use different models
    MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite-preview-06-17")
    
    # Initialize generator
    generator = UQMSchemaGenerator(OPENROUTER_API_KEY, UQM_API_BASE, MODEL)
    
    # Process options
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "single" and len(sys.argv) > 2:
            # Process single query
            query_id = int(sys.argv[2])
            result = generator.process_single_query(query_id)
            if result:
                print(f"Generated: {result}")
        elif sys.argv[1] == "range" and len(sys.argv) > 3:
            # Process range of queries
            start = int(sys.argv[2])
            limit = int(sys.argv[3])
            results = generator.process_all_queries(limit=limit, start_from=start)
            print(f"Generated {len(results)} files")
        else:
            print("Usage:")
            print("  python uqm_schema_generator.py single <query_id>")
            print("  python uqm_schema_generator.py range <start_id> <limit>")
            print("  python uqm_schema_generator.py  (process all)")
    else:
        # Process all queries (first 10 by default for testing)
        results = generator.process_all_queries(limit=10)
        print(f"Generated {len(results)} files")


if __name__ == "__main__":
    main()
