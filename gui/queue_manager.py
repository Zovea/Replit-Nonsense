"""
Queue Manager for handling media processing tasks
"""

import threading
import time
from datetime import datetime
from collections import deque
import uuid

class QueueItem:
    """Represents a single item in the processing queue"""
    
    def __init__(self, source, item_type, options=None):
        self.id = str(uuid.uuid4())
        self.source = source
        self.type = item_type  # "url" or "file"
        self.options = options or {}
        self.status = "queued"  # queued, processing, completed, error
        self.progress = 0.0
        self.error_message = ""
        self.output_file = ""
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        
    def to_dict(self):
        """Convert to dictionary for UI display"""
        return {
            'id': self.id,
            'source': self.source,
            'type': self.type,
            'status': self.status,
            'progress': self.progress,
            'error_message': self.error_message,
            'output_file': self.output_file,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }

class QueueManager:
    """Manages the processing queue for media items"""
    
    def __init__(self, processor):
        self.processor = processor
        self.queue = deque()
        self.processing_items = {}
        self.completed_items = []
        self.error_items = []
        
        self.running = True
        self.queue_lock = threading.Lock()
        self.max_concurrent = 2  # Maximum concurrent processing tasks
        
    def add_item(self, source, item_type, options=None):
        """Add item to processing queue"""
        item = QueueItem(source, item_type, options)
        
        with self.queue_lock:
            self.queue.append(item)
            
        return item.id
        
    def get_queue_items(self):
        """Get all queue items for UI display"""
        items = []
        
        with self.queue_lock:
            # Add queued items
            for item in self.queue:
                items.append(item.to_dict())
                
            # Add processing items
            for item in self.processing_items.values():
                items.append(item.to_dict())
                
            # Add completed items (last 50)
            for item in self.completed_items[-50:]:
                items.append(item.to_dict())
                
            # Add error items (last 50)
            for item in self.error_items[-50:]:
                items.append(item.to_dict())
                
        return sorted(items, key=lambda x: x['created_at'], reverse=True)
        
    def clear_completed(self):
        """Clear completed items from display"""
        with self.queue_lock:
            self.completed_items.clear()
            
    def clear_all(self):
        """Clear all items from queue"""
        with self.queue_lock:
            self.queue.clear()
            self.completed_items.clear()
            self.error_items.clear()
            # Note: Cannot clear currently processing items
            
    def process_queue(self):
        """Main queue processing loop"""
        while self.running:
            try:
                # Check if we can start a new task
                if len(self.processing_items) < self.max_concurrent:
                    with self.queue_lock:
                        if self.queue:
                            item = self.queue.popleft()
                            self.processing_items[item.id] = item
                            
                    if 'item' in locals():
                        # Start processing in a separate thread
                        thread = threading.Thread(
                            target=self._process_item, 
                            args=(item,), 
                            daemon=True
                        )
                        thread.start()
                        
                time.sleep(0.5)  # Small delay to prevent busy waiting
                
            except Exception as e:
                print(f"Error in queue processing: {e}")
                time.sleep(1)
                
    def _process_item(self, item):
        """Process a single queue item"""
        try:
            item.status = "processing"
            item.started_at = datetime.now()
            
            # Create progress callback
            def progress_callback(progress):
                item.progress = progress
                
            # Process the item based on type
            if item.type == "url":
                result = self.processor.process_url(
                    item.source, 
                    item.options, 
                    progress_callback
                )
            elif item.type == "file":
                result = self.processor.process_file(
                    item.source, 
                    item.options, 
                    progress_callback
                )
            else:
                raise ValueError(f"Unknown item type: {item.type}")
                
            # Update item with results
            item.status = "completed"
            item.progress = 100.0
            item.output_file = result.get('output_file', '')
            item.completed_at = datetime.now()
            
            # Move to completed items
            with self.queue_lock:
                if item.id in self.processing_items:
                    del self.processing_items[item.id]
                self.completed_items.append(item)
                
        except Exception as e:
            # Handle processing error
            item.status = "error"
            item.error_message = str(e)
            item.completed_at = datetime.now()
            
            # Move to error items
            with self.queue_lock:
                if item.id in self.processing_items:
                    del self.processing_items[item.id]
                self.error_items.append(item)
                
    def stop(self):
        """Stop the queue manager"""
        self.running = False
        
    def get_stats(self):
        """Get queue statistics"""
        with self.queue_lock:
            return {
                'queued': len(self.queue),
                'processing': len(self.processing_items),
                'completed': len(self.completed_items),
                'errors': len(self.error_items)
            }
