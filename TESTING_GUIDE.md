# 🧪 Testing Guide

## Test Scenarios for Portfolio Demo

### Test 1: Basic Conversation
**Purpose**: Show basic chat functionality without tools

**Steps**:
1. Start the application
2. Send message: "Hello! How are you?"
3. **Expected**: Direct response without tool use
4. **Validates**: LLM integration, basic chat flow

---

### Test 2: Time Query (Single Tool)
**Purpose**: Demonstrate single tool usage

**Steps**:
1. Send message: "What time is it?"
2. **Expected**:
   - Agent uses `get_current_time` tool
   - Returns current timestamp
   - Reasoning trace shows 1-2 iterations
3. **Validates**: Tool selection, tool execution

**Reasoning Trace Example**:
```
Iteration 1:
  Thought: User wants current time
  Action: get_current_time
  Observation: Current date and time: 2024-01-15 14:30:00
  
Iteration 2:
  Answer: The current time is 2:30 PM...
```

---

### Test 3: Document Upload
**Purpose**: Show document processing and RAG system

**Steps**:
1. Click sidebar menu
2. Upload `sample_document.md`
3. **Expected**:
   - Progress bar shows upload
   - Success message with chunk count
   - Document count increases in header
4. **Validates**: File upload, document processing, chunking

---

### Test 4: Document Search (RAG Query)
**Purpose**: Demonstrate semantic search and retrieval

**Steps**:
1. After uploading sample_document.md
2. Send message: "What is machine learning?"
3. **Expected**:
   - Agent uses `search_documents` tool
   - Retrieves relevant chunks from uploaded doc
   - Provides answer based on document content
4. **Validates**: Vector search, RAG pipeline, context retrieval

**Reasoning Trace Example**:
```
Iteration 1:
  Thought: User asking about ML, should search documents
  Action: search_documents
  Action Input: {"query": "machine learning"}
  Observation: Found relevant information:
    1. Machine Learning is a subset of AI...
    
Iteration 2:
  Answer: Based on the documents, machine learning is...
```

---

### Test 5: Multi-Step Reasoning
**Purpose**: Show complex reasoning with multiple tools

**Steps**:
1. Send message: "How many documents do I have and what time is it?"
2. **Expected**:
   - Agent recognizes two separate tasks
   - Uses `summarize_documents` tool
   - Uses `get_current_time` tool
   - Combines results in coherent answer
   - 3-4 iterations
3. **Validates**: Multi-step planning, multiple tool use

**Reasoning Trace Example**:
```
Iteration 1:
  Thought: Two pieces of information needed
  Action: summarize_documents
  Observation: Knowledge base contains 15 chunks
  
Iteration 2:
  Thought: Got documents, now need time
  Action: get_current_time
  Observation: Current time is 2024-01-15 14:30:00
  
Iteration 3:
  Answer: You have 15 document chunks and it's 2:30 PM
```

---

### Test 6: Calculator Tool
**Purpose**: Show calculation capability

**Steps**:
1. Send message: "What is 25 * 4 + 100?"
2. **Expected**:
   - Agent uses `calculate` tool
   - Returns correct answer (200)
3. **Validates**: Mathematical tool, safe expression evaluation

---

### Test 7: Complex Document Query
**Purpose**: Demonstrate advanced RAG

**Steps**:
1. Send message: "What are the different types of machine learning mentioned in my documents?"
2. **Expected**:
   - Searches documents
   - Finds supervised, unsupervised, reinforcement learning
   - Provides detailed explanation from context
3. **Validates**: Semantic understanding, multi-chunk retrieval

---

### Test 8: Tool Selection Logic
**Purpose**: Show agent correctly chooses NOT to use tools when unnecessary

**Steps**:
1. Send message: "Explain what an API is"
2. **Expected**:
   - Agent provides direct answer
   - No tool use (knowledge is in LLM)
   - Quick response
3. **Validates**: Intelligent tool selection, efficiency

---

### Test 9: Error Handling
**Purpose**: Show graceful error handling

**Steps**:
1. Send message: "Calculate 1/0"
2. **Expected**:
   - Tool returns error message
   - Agent handles gracefully
   - Provides explanation
3. **Validates**: Error handling, robustness

---

### Test 10: Streaming Response
**Purpose**: Demonstrate real-time response streaming (if implemented)

**Steps**:
1. Use streaming endpoint if available
2. Send long query
3. **Expected**:
   - Response appears word-by-word
   - Better user experience
4. **Validates**: Async streaming, UX optimization

---

## API Testing

### Using cURL

#### Health Check
```bash
curl http://localhost:8000/health
```
**Expected Response**:
```json
{
  "status": "healthy",
  "service": "Agentic RAG Chatbot"
}
```

#### System Status
```bash
curl http://localhost:8000/status
```
**Expected Response**:
```json
{
  "status": "operational",
  "version": "1.0.0",
  "total_documents": 15,
  "available_tools": [
    "search_documents",
    "get_current_time",
    "calculate",
    "summarize_documents",
    "web_search"
  ]
}
```

#### Chat Request
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What time is it?",
    "conversation_history": [],
    "use_rag": true
  }'
```

#### Document Upload
```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@sample_document.md"
```

#### Document Search
```bash
curl -X POST http://localhost:8000/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "top_k": 5
  }'
```

#### Get Available Tools
```bash
curl http://localhost:8000/tools
```

---

## Performance Testing

### Document Processing Speed
**Test**: Upload various file sizes
- Small (< 100KB): Should process in < 1 second
- Medium (100KB - 1MB): Should process in 1-3 seconds
- Large (> 1MB): Should process in 3-10 seconds

### Query Response Time
**Test**: Measure time from query to response
- Simple queries (no tools): < 2 seconds
- Single tool queries: < 3 seconds
- Multi-tool queries: < 5 seconds
- RAG queries: < 4 seconds

### Vector Search Performance
**Test**: Search speed with different document counts
- 0-100 chunks: < 100ms
- 100-1000 chunks: < 500ms
- 1000+ chunks: < 1 second

---

## Integration Testing

### Test 1: End-to-End Flow
1. Upload document
2. Query document content
3. Verify correct retrieval
4. Check reasoning trace

### Test 2: Conversation Context
1. Send first message
2. Send follow-up referencing previous message
3. Verify context is maintained

### Test 3: Multiple Documents
1. Upload multiple documents
2. Query across all documents
3. Verify retrieval from correct sources

---

## Edge Cases

### Test 1: Empty Query
**Input**: ""
**Expected**: Validation error or prompt to enter message

### Test 2: Very Long Query
**Input**: 2000+ word query
**Expected**: Handles gracefully, may truncate if needed

### Test 3: Unsupported File Type
**Input**: .exe, .zip file
**Expected**: Clear error message about supported formats

### Test 4: No Documents Uploaded
**Input**: "Search my documents"
**Expected**: Informative message that no documents exist

### Test 5: Max Iterations Reached
**Input**: Complex recursive query
**Expected**: Agent stops at max iterations, provides partial answer

---

## User Acceptance Testing

### Usability Tests
- [ ] Can upload documents easily
- [ ] Chat interface is intuitive
- [ ] Reasoning trace is helpful
- [ ] Loading states are clear
- [ ] Error messages are understandable

### Functionality Tests
- [ ] All tools work correctly
- [ ] Document search is accurate
- [ ] Responses are relevant
- [ ] System is responsive
- [ ] No crashes or freezes

### UX Tests
- [ ] Responsive on mobile
- [ ] Works in different browsers
- [ ] Keyboard shortcuts work
- [ ] Accessibility features present

---

## Automated Testing (Future Enhancement)

### Backend Tests
```python
# pytest examples

def test_document_upload():
    response = client.post(
        "/documents/upload",
        files={"file": open("test.pdf", "rb")}
    )
    assert response.status_code == 200
    assert "chunks_created" in response.json()

def test_chat_endpoint():
    response = client.post(
        "/chat",
        json={"message": "Hello", "conversation_history": []}
    )
    assert response.status_code == 200
    assert "answer" in response.json()

def test_vector_search():
    result = vector_store.search("test query", n_results=5)
    assert len(result) <= 5
    assert all("text" in r for r in result)
```

### Frontend Tests
```javascript
// Jest/React Testing Library examples

test('renders chat interface', () => {
  render(<ChatInterface />);
  expect(screen.getByPlaceholderText('Ask me anything...')).toBeInTheDocument();
});

test('sends message on submit', async () => {
  render(<ChatInterface />);
  const input = screen.getByPlaceholderText('Ask me anything...');
  fireEvent.change(input, { target: { value: 'Hello' } });
  fireEvent.submit(input.closest('form'));
  // Assert API call was made
});
```

---

## Demo Script for Portfolio Presentation

### 1. Introduction (30 seconds)
"This is an Agentic RAG Chatbot that combines retrieval-augmented generation with agentic reasoning. It can search documents, use tools, and explain its thought process."

### 2. Document Upload (1 minute)
- Show sidebar
- Upload sample document
- Point out processing feedback
- Show document count update

### 3. RAG Query (1 minute)
- Ask about document content
- Show retrieved context
- Highlight accurate answer

### 4. Agent Reasoning (1 minute)
- Ask multi-step question
- Expand reasoning trace
- Explain ReAct pattern
- Show tool usage

### 5. Code Walkthrough (2 minutes)
- Show agent implementation
- Highlight RAG pipeline
- Point out tool system
- Discuss architecture

### 6. Questions (Remaining time)

---

## Monitoring & Debugging

### Backend Logs
Check terminal for:
- API requests
- Tool executions
- Error messages
- Performance metrics

### Frontend Console
Check browser console for:
- API responses
- Component errors
- Network issues

### Database Inspection
```python
# Check ChromaDB contents
from app.rag.vector_store import vector_store
stats = vector_store.get_collection_stats()
print(f"Total documents: {stats['total_documents']}")
```

---

## Success Criteria

✅ All test scenarios pass  
✅ No critical errors  
✅ Response times acceptable  
✅ UI is responsive  
✅ Reasoning traces are clear  
✅ Document upload works reliably  
✅ RAG retrieval is accurate  
✅ Tools execute correctly  

---

*Use this guide to thoroughly test your chatbot before portfolio presentation*
