"""
MongoDB Client for Healthcare System

Provides connection management and basic database operations for the healthcare chatbot.

Author: Robert Tartarotti
Email: robert.tartarotti@gmail.com
Date: July 22, 2025
"""

from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from .exceptions import ConnectionError, MongoDBError
from .config import MongoDBConfig, get_logger


class MongoDBClient:
    """MongoDB client for healthcare system operations."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize MongoDB client.
        
        Args:
            connection_string: MongoDB connection string. If None, uses configuration.
        """
        self.logger = get_logger("client")
        self.connection_string = connection_string or MongoDBConfig.get_connection_string()
        self.connection_options = MongoDBConfig.get_connection_options()
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        
        self.logger.debug(f"Initialized MongoDB client with connection string: {self.connection_string}")
    
    def connect(self) -> None:
        """
        Establish connection to MongoDB.
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            self.logger.info("Connecting to MongoDB...")
            self.client = MongoClient(self.connection_string, **self.connection_options)
            
            self.client.admin.command('ping')
            self.database = self.client.get_database()
            
            self.logger.info("Successfully connected to MongoDB")
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")
    
    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.logger.info("Disconnecting from MongoDB...")
            self.client.close()
            self.client = None
            self.database = None
            self.logger.info("Disconnected from MongoDB")
    
    def get_collection(self, collection_name: str) -> Collection:
        """
        Get a collection from the database.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection: MongoDB collection object
            
        Raises:
            ConnectionError: If not connected to MongoDB
        """
        if not self.database:
            raise ConnectionError("Not connected to MongoDB")
        return self.database[collection_name]
    
    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """
        Insert a single document into a collection.
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
            
        Returns:
            str: ID of the inserted document
        """
        self.logger.debug(f"Inserting document into collection: {collection_name}")
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        inserted_id = str(result.inserted_id)
        self.logger.debug(f"Inserted document with ID: {inserted_id}")
        return inserted_id
    
    def insert_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple documents into a collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of documents to insert
            
        Returns:
            List[str]: List of IDs of the inserted documents
        """
        self.logger.debug(f"Inserting {len(documents)} documents into collection: {collection_name}")
        collection = self.get_collection(collection_name)
        result = collection.insert_many(documents)
        inserted_ids = [str(id) for id in result.inserted_ids]
        self.logger.debug(f"Inserted {len(inserted_ids)} documents")
        return inserted_ids
    
    def find_one(self, collection_name: str, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document in a collection.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria
            
        Returns:
            Optional[Dict[str, Any]]: Found document or None
        """
        self.logger.debug(f"Finding document in collection: {collection_name} with filter: {filter_dict}")
        collection = self.get_collection(collection_name)
        result = collection.find_one(filter_dict)
        if result:
            self.logger.debug(f"Found document in collection: {collection_name}")
        else:
            self.logger.debug(f"No document found in collection: {collection_name}")
        return result
    
    def find_many(self, collection_name: str, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Find multiple documents in a collection.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria (optional)
            
        Returns:
            List[Dict[str, Any]]: List of found documents
        """
        filter_dict = filter_dict or {}
        self.logger.debug(f"Finding documents in collection: {collection_name} with filter: {filter_dict}")
        collection = self.get_collection(collection_name)
        results = list(collection.find(filter_dict))
        self.logger.debug(f"Found {len(results)} documents in collection: {collection_name}")
        return results
    
    def update_one(self, collection_name: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> int:
        """
        Update a single document in a collection.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria
            update_dict: Update data
            
        Returns:
            int: Number of modified documents
        """
        self.logger.debug(f"Updating document in collection: {collection_name} with filter: {filter_dict}")
        collection = self.get_collection(collection_name)
        result = collection.update_one(filter_dict, {"$set": update_dict})
        modified_count = result.modified_count
        self.logger.debug(f"Updated {modified_count} document(s) in collection: {collection_name}")
        return modified_count
    
    def delete_one(self, collection_name: str, filter_dict: Dict[str, Any]) -> int:
        """
        Delete a single document from a collection.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria
            
        Returns:
            int: Number of deleted documents
        """
        self.logger.debug(f"Deleting document from collection: {collection_name} with filter: {filter_dict}")
        collection = self.get_collection(collection_name)
        result = collection.delete_one(filter_dict)
        deleted_count = result.deleted_count
        self.logger.debug(f"Deleted {deleted_count} document(s) from collection: {collection_name}")
        return deleted_count
    
    def __enter__(self):
        """
        Context manager entry.
        
        Returns:
            MongoDBClient: Self instance
        """
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def main():
    """Main entry point for MongoDB client."""
    import sys
    
    print("Healthcare MongoDB Client")
    print("=========================")
    
    try:
        with MongoDBClient() as client:
            print("✅ Successfully connected to MongoDB")
            
            collections = client.database.list_collection_names()
            print(f"📊 Available collections: {collections}")
            
            for collection_name in collections:
                count = client.database[collection_name].count_documents({})
                print(f"   - {collection_name}: {count} documents")
            
            print("\n🚀 MongoDB client is ready for use!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 