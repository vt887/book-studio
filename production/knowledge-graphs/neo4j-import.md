# Neo4j Import & Setup Guide - Object-Oriented Thinking Knowledge Graph

**Generated:** 2026-04-25T17:00:00Z  
**Graph Version:** 1.0  
**Neo4j Version Required:** 4.4+

---

## Quick Start (5 minutes)

### 1. **Setup Neo4j**

```bash
# Docker (Recommended)
docker run --name oop-kg \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Access at: http://localhost:7474
```

### 2. **Connect & Import**

```bash
# Open Neo4j Browser: http://localhost:7474
# Default: neo4j / password

# Step 1: Copy cypher-production.txt contents
# Step 2: Paste into Neo4j Browser query editor
# Step 3: Execute each phase sequentially

# Expected execution time: <30 seconds
```

### 3. **Verify Import**

```cypher
// Verify all nodes created
MATCH (n) RETURN labels(n)[0] as node_type, COUNT(n) as count
ORDER BY count DESC;

// Expected Output:
// CONCEPT    9
// ADR       12
// TEST      52
// ROLE       4
// PATTERN   13
// Total: 98 nodes ✓
```

---

## Step-by-Step Import Guide

### Phase 1: Preparation

**Check Neo4j is running:**
```cypher
CALL dbms.info() YIELD name, value
RETURN name, value LIMIT 5;
```

**Clear existing data (if re-importing):**
```cypher
MATCH (n) DETACH DELETE n;
// This deletes all nodes and relationships
```

### Phase 2: Create Concept Nodes (Layer 1)

Execute all 9 CREATE statements for CONCEPT nodes from `cypher-production.txt`

```cypher
CREATE (oop:CONCEPT {
  id: 'concept_oop',
  name: 'Object-Oriented Programming',
  // ... properties
});
// ... repeat for 8 more concepts
```

**Verify:**
```cypher
MATCH (c:CONCEPT) RETURN COUNT(c) as concept_count;
// Expected: 9
```

### Phase 3: Create Concept Relationships (Layer 1)

Execute all relationship creation queries (FOUNDATION, ENABLES, IMPLEMENTS, etc.)

```cypher
MATCH (oop:CONCEPT {id: 'concept_oop'}), (class:CONCEPT {id: 'concept_class'})
CREATE (oop)-[r:FOUNDATION {strength: 0.98}]->(class)
SET r.description = 'OOP relies on classes as fundamental building blocks';
// ... repeat for remaining relationships
```

**Verify:**
```cypher
MATCH (c:CONCEPT)-[r]-(other:CONCEPT) 
RETURN COUNT(r) as concept_relationships;
// Expected: 8+
```

### Phase 4: Create ADR Nodes (Layer 2)

Execute all 12 CREATE statements for ADR nodes

```cypher
CREATE (adr001:ADR {
  id: 'adr_001',
  title: 'Abstraction as Primary Design Tool',
  // ... properties
});
// ... repeat for 11 more ADRs
```

**Verify:**
```cypher
MATCH (a:ADR) RETURN COUNT(a) as adr_count;
// Expected: 12
```

### Phase 5: Create ADR → Concept Relationships (Layer 2)

Execute all ADR relationship creation queries

```cypher
MATCH (adr001:ADR {id: 'adr_001'}), (abstraction:CONCEPT {id: 'concept_abstraction'})
CREATE (adr001)-[r:IMPLEMENTS {strength: 0.96}]->(abstraction)
SET r.description = 'ADR-001 implements abstraction principle';
// ... repeat for remaining ADR relationships
```

### Phase 6: Create TEST Nodes (Layer 3)

Execute TEST node creation (sample 6 shown, all 52 in file)

```cypher
CREATE (tc001:TEST {
  id: 'tc_001',
  testId: 'TC-001',
  type: 'unit',
  title: 'Class Definition - Valid Object Creation',
  // ... properties
});
// ... repeat for 51 more tests
```

### Phase 7: Create TEST Relationships

Execute test relationship creation

```cypher
MATCH (tc001:TEST {id: 'tc_001'}), (class:CONCEPT {id: 'concept_class'})
CREATE (tc001)-[r:VALIDATES {strength: 1.0}]->(class)
SET r.description = 'TC-001 validates class definition concept';
// ... repeat for remaining test relationships
```

### Phase 8: Create ROLE Nodes (Layer 4)

Execute all 4 ROLE node creation

```cypher
CREATE (dev:ROLE {
  id: 'role_developer',
  name: 'Developer',
  title: 'Software Developer',
  // ... properties
});
// ... repeat for 3 more roles
```

### Phase 9: Create ROLE → Concept Relationships

Execute role relationship creation

```cypher
MATCH (dev:ROLE {id: 'role_developer'}), (class:CONCEPT {id: 'concept_class'})
CREATE (dev)-[r:HAS {strength: 0.98}]->(class)
SET r.description = 'Developer applies class definition daily';
```

### Phase 10: Create PATTERN Nodes (Layer 5)

Execute all 13 PATTERN node creation

```cypher
CREATE (factory:PATTERN {
  id: 'pattern_factory',
  name: 'Factory Method',
  // ... properties
});
// ... repeat for 12 more patterns
```

### Phase 11: Create PATTERN Relationships

Execute pattern relationship creation

```cypher
MATCH (factory:PATTERN {id: 'pattern_factory'}), (polymorphism:CONCEPT {id: 'concept_polymorphism'})
CREATE (factory)-[r:IMPLEMENTS {strength: 0.92}]->(polymorphism)
SET r.description = 'Factory pattern implements polymorphism';
```

---

## Index & Constraint Setup

### Create Indexes for Performance

```cypher
// Concept indexes
CREATE INDEX idx_concept_name FOR (c:CONCEPT) ON (c.name);
CREATE INDEX idx_concept_importance FOR (c:CONCEPT) ON (c.importance);
CREATE INDEX idx_concept_id FOR (c:CONCEPT) ON (c.id);

// ADR indexes
CREATE INDEX idx_adr_id FOR (a:ADR) ON (a.id);
CREATE INDEX idx_adr_title FOR (a:ADR) ON (a.title);

// Test indexes
CREATE INDEX idx_test_id FOR (t:TEST) ON (t.testId);
CREATE INDEX idx_test_type FOR (t:TEST) ON (t.type);

// Role indexes
CREATE INDEX idx_role_name FOR (r:ROLE) ON (r.name);

// Pattern indexes
CREATE INDEX idx_pattern_name FOR (p:PATTERN) ON (p.name);
CREATE INDEX idx_pattern_category FOR (p:PATTERN) ON (p.category);

// Compound indexes
CREATE INDEX idx_concept_complexity_importance 
  FOR (c:CONCEPT) ON (c.complexity, c.importance);
```

### Create Uniqueness Constraints

```cypher
// Ensure unique identifiers
CREATE CONSTRAINT uniq_concept_id FOR (c:CONCEPT) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT uniq_adr_id FOR (a:ADR) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT uniq_test_id FOR (t:TEST) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT uniq_role_id FOR (r:ROLE) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT uniq_pattern_id FOR (p:PATTERN) REQUIRE p.id IS UNIQUE;
```

---

## Verification Queries

### Graph Integrity Check

```cypher
// 1. Verify node counts
MATCH (n) RETURN labels(n)[0] as type, COUNT(n) as count
ORDER BY count DESC;

// Expected:
// TEST     52
// CONCEPT   9
// ADR      12
// PATTERN  13
// ROLE      4
// Total: 90 ✓

// 2. Verify relationship count
MATCH ()-[r]->() RETURN COUNT(r) as total_relationships;
// Expected: 215

// 3. Check for orphaned nodes
MATCH (n) WHERE NOT (n)-[]-() 
RETURN labels(n)[0] as type, n.name as name, COUNT(*) as count;
// Expected: Should be 1 (OOP with no incoming, multiple outgoing)

// 4. Verify relationship types
MATCH ()-[r]->() RETURN TYPE(r) as rel_type, COUNT(r) as count
ORDER BY count DESC;

// 5. Check data quality
MATCH (c:CONCEPT) WHERE c.importance IS NULL 
RETURN COUNT(c) as concepts_without_importance;
// Expected: 0

// 6. Validate role-concept mappings
MATCH (r:ROLE)-[:HAS]->(c:CONCEPT) 
RETURN r.name as role, COUNT(c) as concepts
ORDER BY concepts DESC;

// 7. Verify test coverage
MATCH (t:TEST)-[:VALIDATES]->(c:CONCEPT) 
RETURN COUNT(DISTINCT c.id) as concepts_covered;
// Expected: 9 (100% of concepts)
```

---

## Common Queries for Exploration

### 1. **Learning Path for Developers**

```cypher
// What should a developer learn first?
MATCH (dev:ROLE {name: 'Developer'})-[:HAS]->(c:CONCEPT)
RETURN c.name as concept, 
       c.importance as importance, 
       c.complexity as complexity
ORDER BY c.complexity, c.importance DESC;
```

### 2. **Find Concepts for Architects**

```cypher
// What are the key concepts for architects?
MATCH (arch:ROLE {name: 'Architect'})-[:HAS]->(c:CONCEPT)
RETURN c.name as concept, 
       arch.applicationScore as role_score,
       c.importance as importance
ORDER BY arch.applicationScore DESC;
```

### 3. **Test Coverage by Concept**

```cypher
// Which concepts have the most test coverage?
MATCH (t:TEST)-[:VALIDATES]->(c:CONCEPT)
RETURN c.name as concept,
       COUNT(t) as test_count,
       COLLECT(t.testId) as tests
ORDER BY test_count DESC;
```

### 4. **ADR Impact Analysis**

```cypher
// Which ADR affects the most concepts?
MATCH (a:ADR)-[:IMPLEMENTS|APPLIES_TO]->(c:CONCEPT)
RETURN a.id as adr,
       a.title as title,
       COUNT(DISTINCT c) as concept_count,
       COLLECT(c.name) as concepts
ORDER BY concept_count DESC;
```

### 5. **Pattern Implementation Map**

```cypher
// How do patterns implement OOP concepts?
MATCH (p:PATTERN)-[:IMPLEMENTS]->(c:CONCEPT)
RETURN p.name as pattern,
       p.category as category,
       c.name as concept,
       c.importance as importance
ORDER BY p.category, p.name;
```

### 6. **Concept Dependencies**

```cypher
// What prerequisites exist for each concept?
MATCH (prerequisite:CONCEPT)-[:FOUNDATION|ENABLES]->(c:CONCEPT)
RETURN c.name as concept,
       COLLECT(prerequisite.name) as prerequisites,
       COUNT(prerequisite) as prerequisite_count
ORDER BY prerequisite_count DESC;
```

### 7. **Role-Specific Patterns**

```cypher
// Which patterns are most relevant to each role?
MATCH (r:ROLE)-[:HAS]->(c:CONCEPT)<-[:IMPLEMENTS|USES]-(p:PATTERN)
RETURN r.name as role,
       p.name as pattern,
       c.name as connection,
       p.category as pattern_type
LIMIT 20;
```

### 8. **Test Quality Metrics**

```cypher
// What's the quality of test coverage?
MATCH (t:TEST)-[:EXERCISES]->(a:ADR)
WITH a, COUNT(t) as test_count
RETURN a.id as adr,
       a.title as title,
       test_count,
       CASE 
         WHEN test_count > 5 THEN '✅ Excellent'
         WHEN test_count > 2 THEN '✅ Good'
         WHEN test_count > 0 THEN '⚠️ Basic'
         ELSE '❌ None'
       END as coverage_level
ORDER BY test_count DESC;
```

### 9. **Concept Centrality**

```cypher
// Which concepts are most connected?
MATCH (c:CONCEPT)-[r]-()
RETURN c.name as concept,
       c.importance as importance,
       COUNT(r) as connectivity
ORDER BY connectivity DESC;
```

### 10. **ADR Implementation Order**

```cypher
// What's the recommended implementation order for ADRs?
MATCH (a:ADR)
OPTIONAL MATCH (a)-[:DEPENDS_ON|REQUIRES]->(prerequisite:ADR)
RETURN a.id as adr,
       a.title as title,
       COUNT(prerequisite) as prerequisites,
       COLLECT(prerequisite.id) as required_adrs
ORDER BY prerequisites ASC, a.id;
```

---

## Dashboard Queries

### Executive Dashboard

```cypher
// Get all key metrics at once
WITH 
  (MATCH (n) RETURN labels(n)[0] as type, COUNT(n) as count) as node_stats,
  (MATCH ()-[r]->() RETURN COUNT(r) as rel_count) as rel_stats,
  (MATCH (c:CONCEPT) RETURN AVG(c.importance) as avg_importance) as concept_avg,
  (MATCH (t:TEST) RETURN COUNT(t) as test_count) as test_stats,
  (MATCH (r:ROLE) RETURN COUNT(r) as role_count) as role_stats

RETURN 'Graph Ready' as status;

// More detailed version:
CALL {
  MATCH (n) RETURN COUNT(n) as total_nodes
}
CALL {
  MATCH ()-[r]->() RETURN COUNT(r) as total_relationships
}
CALL {
  MATCH (c:CONCEPT)-[:FOUNDATION|ENABLES*]->() RETURN COUNT(DISTINCT c) as concept_chains
}
CALL {
  MATCH (a:ADR)-[:IMPLEMENTS|APPLIES_TO]->(c:CONCEPT) 
  RETURN COUNT(DISTINCT a) as adrs_with_concepts
}
CALL {
  MATCH (t:TEST)-[:VALIDATES]->(c:CONCEPT) 
  RETURN COUNT(DISTINCT c) as concepts_with_tests
}

RETURN 
  total_nodes as "Total Nodes",
  total_relationships as "Total Relationships",
  concept_chains as "Concept Chains",
  adrs_with_concepts as "ADRs Implemented",
  concepts_with_tests as "Concepts Tested";
```

---

## Advanced Analysis

### Pattern Strength Analysis

```cypher
// Analyze strength of all relationship types
MATCH ()-[r]->() 
WITH TYPE(r) as relationship_type, 
     COALESCE(r.strength, 1.0) as strength
RETURN relationship_type,
       COUNT(*) as count,
       MIN(strength) as min_strength,
       AVG(strength) as avg_strength,
       MAX(strength) as max_strength
ORDER BY avg_strength DESC;
```

### Concept Maturity Matrix

```cypher
// Categorize concepts by complexity and importance
MATCH (c:CONCEPT)
RETURN 
  CASE 
    WHEN c.complexity = 'simple' AND c.importance > 0.9 THEN 'Quick Wins'
    WHEN c.complexity = 'simple' AND c.importance <= 0.9 THEN 'Basics'
    WHEN c.complexity = 'medium' AND c.importance > 0.9 THEN 'Core Advanced'
    WHEN c.complexity = 'medium' AND c.importance <= 0.9 THEN 'Core Intermediate'
    WHEN c.complexity = 'high' THEN 'Expert Topics'
  END as category,
  COLLECT(c.name) as concepts,
  COUNT(c) as count
ORDER BY category;
```

### Role Readiness Assessment

```cypher
// Assess role readiness by test coverage
MATCH (r:ROLE)
WITH r
MATCH (r)-[:HAS]->(c:CONCEPT)
OPTIONAL MATCH (t:TEST)-[:VALIDATES]->(c)
RETURN r.name as role,
       COUNT(c) as total_concepts,
       COUNT(DISTINCT t) as covered_by_tests,
       ROUND(100.0 * COUNT(DISTINCT t) / COUNT(c), 1) as coverage_percentage
ORDER BY coverage_percentage DESC;
```

---

## Troubleshooting

### Issue: Import Fails on Phase 3

**Problem:** Duplicate node IDs
```
Neo4j.ClientError.Schema.ConstraintValidationFailed
```

**Solution:**
```cypher
// Check for duplicates
MATCH (n) RETURN labels(n)[0] as type, n.id as id, COUNT(*) as count
WHERE count > 1;

// Clear and reimport
MATCH (n) DETACH DELETE n;
```

### Issue: Memory Exceeded

**Problem:** Large import
```
OutOfMemoryError
```

**Solution:**
```bash
# Increase Neo4j heap memory
export NEO4J_HEAP_MEMORY=2048m

# Or in docker
docker run -e NEO4J_HEAP_MEMORY=2048m ...
```

### Issue: Slow Queries

**Problem:** No indexes
```
Query timeout or slow execution
```

**Solution:**
```cypher
// Create all indexes
CREATE INDEX idx_concept_name FOR (c:CONCEPT) ON (c.name);
CREATE INDEX idx_adr_id FOR (a:ADR) ON (a.id);
CREATE INDEX idx_test_id FOR (t:TEST) ON (t.testId);
CREATE INDEX idx_role_name FOR (r:ROLE) ON (r.name);
CREATE INDEX idx_pattern_name FOR (p:PATTERN) ON (p.name);

// Check query plan
EXPLAIN MATCH (c:CONCEPT {name: 'Class Definition'}) RETURN c;
```

---

## Export & Backup

### Export Graph to File

```cypher
// Export as Cypher
:export json file.json

// Or use apoc for more control
CALL apoc.export.json.all("graph.json", {})
YIELD file, source, format, nodes, relationships, properties, time
RETURN *;
```

### Backup Database

```bash
# Docker backup
docker exec <container_id> neo4j-admin dump --database=neo4j --to=/tmp/backup.dump

# Docker restore
docker exec <container_id> neo4j-admin load --database=neo4j --from=/tmp/backup.dump --force
```

---

## Next Steps After Import

1. ✅ **Verify** - Run verification queries (10 min)
2. 📊 **Create Dashboards** - Set up Neo4j Browser dashboards (20 min)
3. 🔍 **Explore** - Run exploration queries (30 min)
4. 📚 **Integrate** - Add to IDE/documentation tools (1-2 hours)
5. 🚀 **Automate** - Create scheduled queries (2-4 hours)

---

## Support & Resources

- **Neo4j Documentation**: https://neo4j.com/docs/
- **Graph Database Queries**: https://neo4j.com/developer/
- **APOC Library**: https://neo4j.com/labs/apoc/
- **Query Performance**: https://neo4j.com/docs/cypher-manual/current/query-tuning/
