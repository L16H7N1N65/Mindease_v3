"""
RAG Performance Profiler and Improvement Area Identifier

This script profiles the current RAG system performance and identifies specific
improvement areas for response accuracy, speed, and semantic relevance.
"""
import sys
import time
import json
import statistics
from typing import Dict, List, Any, Tuple
import numpy as np
from collections import defaultdict

# Add the app directory to Python path
sys.path.append('/workspace/backend/mindease-api')

from app.services.embedding_service import EmbeddingService
from app.services.document_search_service import DocumentSearchService
from app.db.session import SessionLocal

class RAGPerformanceProfiler:
    """Comprehensive RAG performance profiling and improvement identification."""
    
    def __init__(self):
        """Initialize profiler components."""
        self.embedding_service = EmbeddingService()
        self.db = SessionLocal()
        self.search_service = DocumentSearchService(self.db, self.embedding_service)
        
        # Mental health test dataset
        self.test_documents = [
            {
                "id": 1,
                "title": "Understanding Anxiety Disorders",
                "content": "Anxiety disorders are characterized by excessive fear, worry, and related behavioral disturbances. Common types include generalized anxiety disorder (GAD), panic disorder, social anxiety disorder, and specific phobias. Symptoms may include restlessness, fatigue, difficulty concentrating, irritability, muscle tension, and sleep disturbances. Treatment typically involves cognitive-behavioral therapy (CBT), exposure therapy, and sometimes medication such as SSRIs or benzodiazepines.",
                "category": "anxiety",
                "keywords": ["anxiety", "fear", "worry", "panic", "phobia", "GAD", "CBT", "therapy"],
                "clinical_relevance": 0.9
            },
            {
                "id": 2,
                "title": "Depression: Symptoms and Evidence-Based Treatments",
                "content": "Major depressive disorder (MDD) is characterized by persistent sadness, loss of interest or pleasure, and various cognitive and physical symptoms. Key symptoms include depressed mood, anhedonia, weight changes, sleep disturbances, fatigue, feelings of worthlessness, concentration difficulties, and suicidal ideation. Evidence-based treatments include cognitive-behavioral therapy, interpersonal therapy, behavioral activation, and antidepressant medications like SSRIs, SNRIs, and tricyclics.",
                "category": "depression",
                "keywords": ["depression", "MDD", "sadness", "anhedonia", "suicidal", "CBT", "antidepressants"],
                "clinical_relevance": 0.95
            },
            {
                "id": 3,
                "title": "Cognitive Behavioral Therapy Techniques",
                "content": "Cognitive Behavioral Therapy (CBT) is an evidence-based psychotherapy that focuses on identifying and changing negative thought patterns and behaviors. Core techniques include cognitive restructuring, behavioral activation, exposure therapy, thought records, activity scheduling, and homework assignments. CBT has strong empirical support for treating depression, anxiety disorders, PTSD, OCD, and many other mental health conditions. The therapy typically involves 12-20 sessions and emphasizes collaboration between therapist and client.",
                "category": "therapy",
                "keywords": ["CBT", "cognitive", "behavioral", "therapy", "restructuring", "exposure", "thought records"],
                "clinical_relevance": 0.85
            },
            {
                "id": 4,
                "title": "Mindfulness and Meditation for Mental Health",
                "content": "Mindfulness-based interventions have shown significant benefits for mental health. Mindfulness involves paying attention to the present moment without judgment. Techniques include mindful breathing, body scans, loving-kindness meditation, and mindful movement. Research demonstrates effectiveness for reducing anxiety, depression, stress, and improving emotional regulation. Mindfulness-Based Stress Reduction (MBSR) and Mindfulness-Based Cognitive Therapy (MBCT) are structured programs with strong evidence bases.",
                "category": "mindfulness",
                "keywords": ["mindfulness", "meditation", "MBSR", "MBCT", "breathing", "present moment"],
                "clinical_relevance": 0.8
            },
            {
                "id": 5,
                "title": "Crisis Intervention and Suicide Prevention",
                "content": "Crisis intervention involves immediate, short-term assistance for individuals experiencing mental health emergencies. Key principles include ensuring safety, providing support, and facilitating access to resources. Warning signs of suicide include talking about death, giving away possessions, sudden mood changes, and social withdrawal. Intervention strategies include active listening, risk assessment, safety planning, and connecting to professional help. Crisis hotlines and emergency services are critical resources.",
                "category": "crisis",
                "keywords": ["crisis", "suicide", "emergency", "safety", "intervention", "hotline", "risk assessment"],
                "clinical_relevance": 1.0
            }
        ]
        
        # Diverse query types for testing
        self.test_queries = [
            # Direct symptom queries
            {
                "query": "I'm feeling anxious and can't stop worrying",
                "expected_categories": ["anxiety"],
                "query_type": "symptom_description",
                "urgency": "medium"
            },
            {
                "query": "I feel sad all the time and have lost interest in everything",
                "expected_categories": ["depression"],
                "query_type": "symptom_description", 
                "urgency": "high"
            },
            # Treatment seeking queries
            {
                "query": "What therapy techniques can help with negative thoughts?",
                "expected_categories": ["therapy", "depression", "anxiety"],
                "query_type": "treatment_seeking",
                "urgency": "low"
            },
            {
                "query": "How does cognitive behavioral therapy work?",
                "expected_categories": ["therapy"],
                "query_type": "information_seeking",
                "urgency": "low"
            },
            # Crisis queries
            {
                "query": "I'm having thoughts of hurting myself",
                "expected_categories": ["crisis"],
                "query_type": "crisis",
                "urgency": "critical"
            },
            # Coping strategy queries
            {
                "query": "What are some mindfulness exercises I can try?",
                "expected_categories": ["mindfulness"],
                "query_type": "coping_strategies",
                "urgency": "low"
            },
            # Complex queries
            {
                "query": "I have both anxiety and depression, what treatments work for both?",
                "expected_categories": ["anxiety", "depression", "therapy"],
                "query_type": "complex_comorbid",
                "urgency": "medium"
            }
        ]
    
    def profile_response_accuracy(self) -> Dict[str, Any]:
        """Profile response accuracy and relevance."""
        print("🎯 Profiling response accuracy...")
        
        accuracy_results = {
            "test_name": "Response Accuracy Profiling",
            "total_queries": len(self.test_queries),
            "query_results": [],
            "accuracy_metrics": {},
            "category_performance": defaultdict(list),
            "urgency_performance": defaultdict(list)
        }
        
        for query_data in self.test_queries:
            query = query_data["query"]
            expected_categories = query_data["expected_categories"]
            query_type = query_data["query_type"]
            urgency = query_data["urgency"]
            
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(query)
            
            # Calculate similarities with all documents
            similarities = []
            for doc in self.test_documents:
                doc_embedding = self.embedding_service.generate_embedding(doc["content"])
                similarity = self.embedding_service.similarity(query_embedding, doc_embedding)
                similarities.append({
                    "document_id": doc["id"],
                    "title": doc["title"],
                    "category": doc["category"],
                    "similarity": similarity,
                    "clinical_relevance": doc["clinical_relevance"]
                })
            
            # Sort by similarity
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            top_3_results = similarities[:3]
            
            # Calculate accuracy metrics
            top_1_category_match = top_3_results[0]["category"] in expected_categories
            top_3_category_matches = sum(1 for result in top_3_results if result["category"] in expected_categories)
            
            # Calculate relevance score (weighted by clinical relevance)
            relevance_score = sum(
                result["similarity"] * result["clinical_relevance"] 
                for result in top_3_results
            ) / 3
            
            query_result = {
                "query": query,
                "query_type": query_type,
                "urgency": urgency,
                "expected_categories": expected_categories,
                "top_results": top_3_results,
                "top_1_accuracy": top_1_category_match,
                "top_3_accuracy": top_3_category_matches / len(expected_categories),
                "relevance_score": relevance_score,
                "max_similarity": top_3_results[0]["similarity"],
                "avg_similarity": statistics.mean([r["similarity"] for r in top_3_results])
            }
            
            accuracy_results["query_results"].append(query_result)
            accuracy_results["category_performance"][query_type].append(query_result["top_1_accuracy"])
            accuracy_results["urgency_performance"][urgency].append(query_result["relevance_score"])
        
        # Calculate overall metrics
        accuracy_results["accuracy_metrics"] = {
            "top_1_accuracy": statistics.mean([r["top_1_accuracy"] for r in accuracy_results["query_results"]]),
            "top_3_accuracy": statistics.mean([r["top_3_accuracy"] for r in accuracy_results["query_results"]]),
            "avg_relevance_score": statistics.mean([r["relevance_score"] for r in accuracy_results["query_results"]]),
            "avg_max_similarity": statistics.mean([r["max_similarity"] for r in accuracy_results["query_results"]]),
            "similarity_std": statistics.stdev([r["max_similarity"] for r in accuracy_results["query_results"]])
        }
        
        return accuracy_results
    
    def profile_response_speed(self) -> Dict[str, Any]:
        """Profile response speed and performance bottlenecks."""
        print("⚡ Profiling response speed...")
        
        speed_results = {
            "test_name": "Response Speed Profiling",
            "performance_metrics": {},
            "bottleneck_analysis": {},
            "speed_by_operation": {}
        }
        
        # Test embedding generation speed
        embedding_times = []
        for _ in range(10):
            start_time = time.time()
            self.embedding_service.generate_embedding("Test query for speed measurement")
            embedding_times.append((time.time() - start_time) * 1000)  # Convert to ms
        
        # Test batch embedding speed
        batch_texts = [doc["content"] for doc in self.test_documents]
        start_time = time.time()
        batch_embeddings = self.embedding_service.generate_embeddings(batch_texts)
        batch_time = (time.time() - start_time) * 1000
        
        # Test similarity calculation speed
        similarity_times = []
        embedding1 = self.embedding_service.generate_embedding("Test text 1")
        embedding2 = self.embedding_service.generate_embedding("Test text 2")
        
        for _ in range(100):
            start_time = time.time()
            self.embedding_service.similarity(embedding1, embedding2)
            similarity_times.append((time.time() - start_time) * 1000)
        
        # Test full search pipeline speed
        pipeline_times = []
        for query_data in self.test_queries[:3]:  # Test first 3 queries
            start_time = time.time()
            
            # Full pipeline simulation
            query_embedding = self.embedding_service.generate_embedding(query_data["query"])
            similarities = []
            for doc in self.test_documents:
                doc_embedding = self.embedding_service.generate_embedding(doc["content"])
                similarity = self.embedding_service.similarity(query_embedding, doc_embedding)
                similarities.append(similarity)
            
            pipeline_time = (time.time() - start_time) * 1000
            pipeline_times.append(pipeline_time)
        
        speed_results["performance_metrics"] = {
            "avg_embedding_time_ms": statistics.mean(embedding_times),
            "embedding_time_std_ms": statistics.stdev(embedding_times),
            "batch_embedding_time_ms": batch_time,
            "batch_efficiency": batch_time / len(batch_texts),  # ms per document
            "avg_similarity_time_ms": statistics.mean(similarity_times),
            "avg_pipeline_time_ms": statistics.mean(pipeline_times),
            "pipeline_time_std_ms": statistics.stdev(pipeline_times)
        }
        
        speed_results["speed_by_operation"] = {
            "embedding_generation": {
                "avg_time_ms": statistics.mean(embedding_times),
                "percentile_95_ms": np.percentile(embedding_times, 95),
                "throughput_per_sec": 1000 / statistics.mean(embedding_times)
            },
            "similarity_calculation": {
                "avg_time_ms": statistics.mean(similarity_times),
                "percentile_95_ms": np.percentile(similarity_times, 95),
                "throughput_per_sec": 1000 / statistics.mean(similarity_times)
            },
            "full_pipeline": {
                "avg_time_ms": statistics.mean(pipeline_times),
                "percentile_95_ms": np.percentile(pipeline_times, 95),
                "queries_per_sec": 1000 / statistics.mean(pipeline_times)
            }
        }
        
        # Identify bottlenecks
        bottlenecks = []
        if statistics.mean(embedding_times) > 100:  # > 100ms per embedding
            bottlenecks.append("Slow embedding generation")
        if batch_time / len(batch_texts) > statistics.mean(embedding_times) * 1.5:
            bottlenecks.append("Inefficient batch processing")
        if statistics.mean(pipeline_times) > 1000:  # > 1 second per query
            bottlenecks.append("Slow overall pipeline")
        
        speed_results["bottleneck_analysis"] = {
            "identified_bottlenecks": bottlenecks,
            "embedding_efficiency": "Good" if statistics.mean(embedding_times) < 50 else "Needs improvement",
            "pipeline_efficiency": "Good" if statistics.mean(pipeline_times) < 500 else "Needs improvement"
        }
        
        return speed_results
    
    def analyze_semantic_relevance_gaps(self) -> Dict[str, Any]:
        """Analyze gaps in semantic relevance and embedding quality."""
        print("🔍 Analyzing semantic relevance gaps...")
        
        relevance_analysis = {
            "test_name": "Semantic Relevance Gap Analysis",
            "embedding_quality": {},
            "semantic_gaps": [],
            "category_analysis": {},
            "improvement_opportunities": []
        }
        
        # Analyze embedding quality
        embeddings = []
        for doc in self.test_documents:
            embedding = self.embedding_service.generate_embedding(doc["content"])
            embeddings.append(embedding)
        
        # Calculate embedding statistics
        embedding_matrix = np.array(embeddings)
        embedding_norms = np.linalg.norm(embedding_matrix, axis=1)
        embedding_similarities = np.corrcoef(embedding_matrix)
        
        relevance_analysis["embedding_quality"] = {
            "avg_norm": float(np.mean(embedding_norms)),
            "norm_std": float(np.std(embedding_norms)),
            "avg_inter_doc_similarity": float(np.mean(embedding_similarities[np.triu_indices_from(embedding_similarities, k=1)])),
            "embedding_dimension": len(embeddings[0]),
            "norm_consistency": float(np.std(embedding_norms) / np.mean(embedding_norms))  # Coefficient of variation
        }
        
        # Analyze category-specific performance
        category_performance = {}
        for category in set(doc["category"] for doc in self.test_documents):
            category_docs = [doc for doc in self.test_documents if doc["category"] == category]
            category_queries = [q for q in self.test_queries if category in q["expected_categories"]]
            
            if category_queries:
                category_similarities = []
                for query_data in category_queries:
                    query_embedding = self.embedding_service.generate_embedding(query_data["query"])
                    for doc in category_docs:
                        doc_embedding = self.embedding_service.generate_embedding(doc["content"])
                        similarity = self.embedding_service.similarity(query_embedding, doc_embedding)
                        category_similarities.append(similarity)
                
                category_performance[category] = {
                    "avg_similarity": statistics.mean(category_similarities) if category_similarities else 0,
                    "similarity_std": statistics.stdev(category_similarities) if len(category_similarities) > 1 else 0,
                    "doc_count": len(category_docs),
                    "query_count": len(category_queries)
                }
        
        relevance_analysis["category_analysis"] = category_performance
        
        # Identify semantic gaps
        gaps = []
        
        # Low overall similarity threshold
        overall_similarities = []
        for query_data in self.test_queries:
            query_embedding = self.embedding_service.generate_embedding(query_data["query"])
            for doc in self.test_documents:
                doc_embedding = self.embedding_service.generate_embedding(doc["content"])
                similarity = self.embedding_service.similarity(query_embedding, doc_embedding)
                overall_similarities.append(similarity)
        
        avg_similarity = statistics.mean(overall_similarities)
        if avg_similarity < 0.3:
            gaps.append({
                "gap_type": "Low Overall Similarity",
                "severity": "High",
                "description": f"Average similarity {avg_similarity:.3f} below threshold 0.3",
                "impact": "Poor document retrieval quality"
            })
        
        # Category-specific gaps
        for category, perf in category_performance.items():
            if perf["avg_similarity"] < 0.25:
                gaps.append({
                    "gap_type": "Category-Specific Low Performance",
                    "severity": "Medium",
                    "category": category,
                    "description": f"Category '{category}' avg similarity {perf['avg_similarity']:.3f}",
                    "impact": f"Poor retrieval for {category}-related queries"
                })
        
        # Embedding consistency issues
        if relevance_analysis["embedding_quality"]["norm_consistency"] > 0.3:
            gaps.append({
                "gap_type": "Inconsistent Embedding Norms",
                "severity": "Medium", 
                "description": f"High norm variation (CV: {relevance_analysis['embedding_quality']['norm_consistency']:.3f})",
                "impact": "Inconsistent similarity calculations"
            })
        
        relevance_analysis["semantic_gaps"] = gaps
        
        # Generate improvement opportunities
        improvements = []
        
        if avg_similarity < 0.3:
            improvements.append("Upgrade to a better pre-trained embedding model (e.g., all-MiniLM-L12-v2)")
        
        if relevance_analysis["embedding_quality"]["norm_consistency"] > 0.3:
            improvements.append("Implement embedding normalization for consistent similarity calculations")
        
        if any(perf["avg_similarity"] < 0.25 for perf in category_performance.values()):
            improvements.append("Fine-tune embeddings on mental health domain-specific data")
        
        improvements.append("Implement query expansion with mental health synonyms")
        improvements.append("Add document preprocessing to improve content quality")
        improvements.append("Consider hybrid search combining semantic and keyword matching")
        
        relevance_analysis["improvement_opportunities"] = improvements
        
        return relevance_analysis
    
    def evaluate_mental_health_context_representation(self) -> Dict[str, Any]:
        """Evaluate how well embeddings represent mental health context."""
        print("🧠 Evaluating mental health context representation...")
        
        context_analysis = {
            "test_name": "Mental Health Context Representation",
            "domain_coverage": {},
            "clinical_term_analysis": {},
            "context_preservation": {},
            "recommendations": []
        }
        
        # Define mental health domain terms
        clinical_terms = {
            "symptoms": ["anxiety", "depression", "panic", "worry", "sadness", "anhedonia", "insomnia"],
            "treatments": ["therapy", "CBT", "medication", "SSRI", "counseling", "psychotherapy"],
            "conditions": ["GAD", "MDD", "PTSD", "OCD", "bipolar", "schizophrenia"],
            "interventions": ["mindfulness", "meditation", "exposure", "cognitive restructuring"],
            "crisis": ["suicide", "self-harm", "crisis", "emergency", "safety"]
        }
        
        # Test domain term representation
        domain_similarities = {}
        for domain, terms in clinical_terms.items():
            term_embeddings = []
            for term in terms:
                embedding = self.embedding_service.generate_embedding(term)
                term_embeddings.append(embedding)
            
            # Calculate intra-domain similarities
            intra_similarities = []
            for i in range(len(term_embeddings)):
                for j in range(i+1, len(term_embeddings)):
                    similarity = self.embedding_service.similarity(term_embeddings[i], term_embeddings[j])
                    intra_similarities.append(similarity)
            
            domain_similarities[domain] = {
                "avg_intra_similarity": statistics.mean(intra_similarities) if intra_similarities else 0,
                "term_count": len(terms),
                "coherence_score": statistics.mean(intra_similarities) if intra_similarities else 0
            }
        
        context_analysis["domain_coverage"] = domain_similarities
        
        # Test clinical term vs general term distinction
        general_terms = ["happy", "car", "computer", "food", "weather", "sports", "music"]
        clinical_term_list = [term for terms in clinical_terms.values() for term in terms]
        
        clinical_embeddings = [self.embedding_service.generate_embedding(term) for term in clinical_term_list]
        general_embeddings = [self.embedding_service.generate_embedding(term) for term in general_terms]
        
        # Calculate cross-domain similarities
        cross_similarities = []
        for clinical_emb in clinical_embeddings:
            for general_emb in general_embeddings:
                similarity = self.embedding_service.similarity(clinical_emb, general_emb)
                cross_similarities.append(similarity)
        
        # Calculate within clinical domain similarities
        clinical_similarities = []
        for i in range(len(clinical_embeddings)):
            for j in range(i+1, len(clinical_embeddings)):
                similarity = self.embedding_service.similarity(clinical_embeddings[i], clinical_embeddings[j])
                clinical_similarities.append(similarity)
        
        context_analysis["clinical_term_analysis"] = {
            "avg_clinical_similarity": statistics.mean(clinical_similarities),
            "avg_cross_domain_similarity": statistics.mean(cross_similarities),
            "domain_separation": statistics.mean(clinical_similarities) - statistics.mean(cross_similarities),
            "clinical_coherence": "Good" if statistics.mean(clinical_similarities) > statistics.mean(cross_similarities) else "Poor"
        }
        
        # Test context preservation in longer texts
        context_texts = [
            "The patient reports feeling anxious and worried about upcoming therapy sessions",
            "Cognitive behavioral therapy techniques help with negative thought patterns",
            "Crisis intervention is needed when someone expresses suicidal ideation"
        ]
        
        context_preservation_scores = []
        for text in context_texts:
            text_embedding = self.embedding_service.generate_embedding(text)
            
            # Extract key clinical terms from text
            text_terms = []
            for term in clinical_term_list:
                if term.lower() in text.lower():
                    text_terms.append(term)
            
            if text_terms:
                # Calculate how well the text embedding represents its clinical terms
                term_similarities = []
                for term in text_terms:
                    term_embedding = self.embedding_service.generate_embedding(term)
                    similarity = self.embedding_service.similarity(text_embedding, term_embedding)
                    term_similarities.append(similarity)
                
                context_preservation_scores.append(statistics.mean(term_similarities))
        
        context_analysis["context_preservation"] = {
            "avg_preservation_score": statistics.mean(context_preservation_scores) if context_preservation_scores else 0,
            "texts_analyzed": len(context_texts),
            "preservation_quality": "Good" if statistics.mean(context_preservation_scores) > 0.3 else "Poor"
        }
        
        # Generate recommendations
        recommendations = []
        
        if context_analysis["clinical_term_analysis"]["domain_separation"] < 0.1:
            recommendations.append("Embeddings don't distinguish well between clinical and general terms - consider domain-specific fine-tuning")
        
        if context_analysis["context_preservation"]["avg_preservation_score"] < 0.3:
            recommendations.append("Poor context preservation in longer texts - consider using sentence-level embeddings")
        
        for domain, metrics in domain_similarities.items():
            if metrics["coherence_score"] < 0.2:
                recommendations.append(f"Low coherence in {domain} domain - improve domain-specific vocabulary")
        
        recommendations.append("Consider implementing mental health ontology-based query expansion")
        recommendations.append("Add clinical terminology normalization preprocessing")
        
        context_analysis["recommendations"] = recommendations
        
        return context_analysis
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive improvement area identification."""
        print("🚀 Starting comprehensive RAG improvement analysis...")
        
        analysis_results = {
            "analysis_timestamp": time.time(),
            "overall_assessment": {},
            "detailed_analyses": {},
            "priority_improvements": [],
            "implementation_roadmap": {}
        }
        
        # Run all analyses
        print("\n" + "="*60)
        accuracy_results = self.profile_response_accuracy()
        print("\n" + "="*60)
        speed_results = self.profile_response_speed()
        print("\n" + "="*60)
        relevance_results = self.analyze_semantic_relevance_gaps()
        print("\n" + "="*60)
        context_results = self.evaluate_mental_health_context_representation()
        print("\n" + "="*60)
        
        analysis_results["detailed_analyses"] = {
            "accuracy": accuracy_results,
            "speed": speed_results,
            "relevance": relevance_results,
            "context": context_results
        }
        
        # Generate overall assessment
        overall_scores = {
            "accuracy_score": accuracy_results["accuracy_metrics"]["top_1_accuracy"],
            "speed_score": min(1.0, 500 / speed_results["performance_metrics"]["avg_pipeline_time_ms"]),  # Normalize to 500ms target
            "relevance_score": relevance_results["embedding_quality"]["avg_inter_doc_similarity"],
            "context_score": context_results["context_preservation"]["avg_preservation_score"]
        }
        
        overall_score = statistics.mean(overall_scores.values())
        
        analysis_results["overall_assessment"] = {
            "overall_score": overall_score,
            "component_scores": overall_scores,
            "grade": "A" if overall_score > 0.8 else "B" if overall_score > 0.6 else "C" if overall_score > 0.4 else "D",
            "status": "Excellent" if overall_score > 0.8 else "Good" if overall_score > 0.6 else "Needs Improvement" if overall_score > 0.4 else "Critical Issues"
        }
        
        # Prioritize improvements
        improvements = []
        
        # Critical issues (score < 0.3)
        if overall_scores["accuracy_score"] < 0.3:
            improvements.append({
                "priority": "Critical",
                "area": "Response Accuracy",
                "issue": "Very low retrieval accuracy",
                "impact": "Users get irrelevant responses",
                "solution": "Upgrade embedding model and implement proper sentence-transformers"
            })
        
        if overall_scores["relevance_score"] < 0.3:
            improvements.append({
                "priority": "Critical", 
                "area": "Semantic Relevance",
                "issue": "Poor semantic understanding",
                "impact": "Documents not properly matched to queries",
                "solution": "Install proper embedding model and fine-tune on mental health data"
            })
        
        # High priority issues (score < 0.5)
        if overall_scores["speed_score"] < 0.5:
            improvements.append({
                "priority": "High",
                "area": "Response Speed",
                "issue": "Slow query processing",
                "impact": "Poor user experience",
                "solution": "Optimize embedding generation and implement caching"
            })
        
        if overall_scores["context_score"] < 0.5:
            improvements.append({
                "priority": "High",
                "area": "Mental Health Context",
                "issue": "Poor domain-specific understanding",
                "impact": "Inaccurate clinical responses",
                "solution": "Fine-tune on mental health corpus and add domain vocabulary"
            })
        
        # Medium priority improvements
        improvements.extend([
            {
                "priority": "Medium",
                "area": "Query Understanding",
                "issue": "Limited query expansion",
                "impact": "Missed relevant documents",
                "solution": "Implement synonym expansion and query reformulation"
            },
            {
                "priority": "Medium",
                "area": "Document Processing",
                "issue": "Basic text preprocessing",
                "impact": "Suboptimal embedding quality",
                "solution": "Advanced text cleaning and clinical term normalization"
            }
        ])
        
        analysis_results["priority_improvements"] = sorted(improvements, key=lambda x: {"Critical": 0, "High": 1, "Medium": 2}[x["priority"]])
        
        # Create implementation roadmap
        roadmap = {
            "phase_1_critical": [imp for imp in improvements if imp["priority"] == "Critical"],
            "phase_2_high": [imp for imp in improvements if imp["priority"] == "High"],
            "phase_3_medium": [imp for imp in improvements if imp["priority"] == "Medium"],
            "estimated_timeline": {
                "phase_1": "1-2 weeks",
                "phase_2": "2-3 weeks", 
                "phase_3": "3-4 weeks"
            }
        }
        
        analysis_results["implementation_roadmap"] = roadmap
        
        return analysis_results

if __name__ == "__main__":
    profiler = RAGPerformanceProfiler()
    results = profiler.run_comprehensive_analysis()
    
    # Print comprehensive results
    print("\n" + "="*80)
    print("RAG IMPROVEMENT AREA IDENTIFICATION RESULTS")
    print("="*80)
    
    print(f"\nOverall Assessment:")
    print(f"Score: {results['overall_assessment']['overall_score']:.3f}")
    print(f"Grade: {results['overall_assessment']['grade']}")
    print(f"Status: {results['overall_assessment']['status']}")
    
    print(f"\nComponent Scores:")
    for component, score in results['overall_assessment']['component_scores'].items():
        print(f"  {component}: {score:.3f}")
    
    print(f"\nPriority Improvements:")
    for improvement in results['priority_improvements']:
        print(f"\n{improvement['priority']} Priority - {improvement['area']}:")
        print(f"  Issue: {improvement['issue']}")
        print(f"  Impact: {improvement['impact']}")
        print(f"  Solution: {improvement['solution']}")
    
    print(f"\nImplementation Roadmap:")
    for phase, timeline in results['implementation_roadmap']['estimated_timeline'].items():
        improvements_count = len(results['implementation_roadmap'][f"{phase}_critical" if "1" in phase else f"{phase}_high" if "2" in phase else f"{phase}_medium"])
        print(f"  {phase.title()}: {improvements_count} improvements ({timeline})")
    
    print("\n" + "="*80)

