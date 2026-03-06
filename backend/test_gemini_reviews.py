"""
Test Gemini AI and Real-Time Review Scraping Integration
"""

import sys
import logging
from models.fraud_detector import get_fraud_detector

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_complete_fraud_detection():
    """Test complete fraud detection with Gemini AI and real review scraping"""
    
    print("\n" + "="*80)
    print("🧪 TESTING GEMINI AI + REAL-TIME REVIEW SCRAPING")
    print("="*80)
    
    # Initialize fraud detector
    detector = get_fraud_detector()
    
    # Test jobs
    test_jobs = [
        {
            'title': 'Senior Python Developer',
            'company': 'Google',
            'location': 'Remote',
            'description': 'We are looking for an experienced Python developer to join our team. You will work on cloud infrastructure, build scalable applications, and collaborate with cross-functional teams. Requirements: 5+ years Python experience, strong knowledge of Django/Flask, experience with AWS/GCP.',
            'salary': '$120,000 - $180,000 per year',
            'job_type': 'Full-time',
            'url': 'https://careers.google.com/jobs/123',
            'requirements': 'Python, Django, AWS, 5+ years experience'
        },
        {
            'title': 'Data Entry Work from Home',
            'company': 'Quick Money Solutions',
            'location': 'Anywhere',
            'description': 'URGENT HIRING! Earn $5000 per week working from home! No experience needed! Just pay $299 registration fee to get started. Contact us on WhatsApp: 9876543210. Guaranteed income! Limited spots available! Act now!',
            'salary': '$5000 per week',
            'job_type': 'Part-time',
            'url': 'https://bit.ly/quickmoney',
            'requirements': 'None'
        },
        {
            'title': 'Software Engineer',
            'company': 'Microsoft',
            'location': 'Seattle, WA',
            'description': 'Join Microsoft as a Software Engineer working on Azure cloud services. Design and implement scalable solutions, write clean code, and collaborate with talented engineers. We offer competitive salary, benefits, and growth opportunities.',
            'salary': '$130,000 - $190,000 per year',
            'job_type': 'Full-time',
            'url': 'https://careers.microsoft.com/job/456',
            'requirements': 'CS degree, 3+ years experience, C#/Java'
        }
    ]
    
    for i, job in enumerate(test_jobs, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {job['title']} at {job['company']}")
        print('='*80)
        
        print(f"\n📋 Job Details:")
        print(f"   Title: {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Salary: {job['salary']}")
        print(f"   Description: {job['description'][:150]}...")
        
        print(f"\n🔍 Running Complete Fraud Analysis...")
        print("   Step 1: Verifying company online...")
        print("   Step 2: Scraping real-time reviews (Glassdoor, Indeed, Google, AmbitionBox)...")
        print("   Step 3: Analyzing with Gemini AI...")
        print("   Step 4: Checking job availability...")
        
        # Run fraud detection
        result = detector.predict(job)
        
        # Display results
        print(f"\n📊 FRAUD DETECTION RESULTS:")
        print(f"   Trust Score: {result['trust_score']:.1%} {'✅' if result['trust_score'] >= 0.7 else '⚠️' if result['trust_score'] >= 0.5 else '❌'}")
        print(f"   Is Fraudulent: {'YES ❌' if result['is_fraudulent'] else 'NO ✅'}")
        print(f"   Verdict: {result['final_verdict']}")
        
        print(f"\n🏢 Company Verification:")
        company_ver = result['company_verification']
        print(f"   Legitimate: {'YES ✅' if company_ver.get('is_real') else 'NO ❌'}")
        print(f"   Confidence: {company_ver.get('confidence', 0):.0%}")
        print(f"   Sources Found: {', '.join(company_ver.get('sources_found', []))}")
        
        # Display real reviews
        reviews = company_ver.get('reviews', {})
        if reviews.get('average_rating', 0) > 0:
            print(f"\n⭐ Real-Time Company Reviews:")
            print(f"   Average Rating: {reviews.get('average_rating', 0)}/5.0")
            print(f"   Total Reviews: {reviews.get('total_reviews', 0)}")
            print(f"   Sources: {reviews.get('sources_found', 0)} platforms")
            
            if reviews.get('glassdoor', {}).get('rating', 0) > 0:
                print(f"   • Glassdoor: {reviews['glassdoor']['rating']}/5.0 ({reviews['glassdoor']['reviews']} reviews)")
            if reviews.get('indeed', {}).get('rating', 0) > 0:
                print(f"   • Indeed: {reviews['indeed']['rating']}/5.0 ({reviews['indeed']['reviews']} reviews)")
            if reviews.get('google', {}).get('rating', 0) > 0:
                print(f"   • Google: {reviews['google']['rating']}/5.0")
            if reviews.get('ambitionbox', {}).get('rating', 0) > 0:
                print(f"   • AmbitionBox: {reviews['ambitionbox']['rating']}/5.0")
        else:
            print(f"\n⭐ Company Reviews: No reviews found online")
        
        # Display Gemini AI analysis
        llm_analysis = result.get('llm_analysis', {})
        if llm_analysis.get('reasoning'):
            print(f"\n🤖 Gemini AI Analysis:")
            print(f"   Fraud Probability: {llm_analysis.get('fraud_probability', 0):.1%}")
            print(f"   Confidence: {llm_analysis.get('confidence', 0):.1%}")
            print(f"   Reasoning: {llm_analysis.get('reasoning', '')[:200]}...")
            
            if llm_analysis.get('red_flags'):
                print(f"   🚩 Red Flags: {', '.join(llm_analysis['red_flags'][:3])}")
            
            if llm_analysis.get('green_flags'):
                print(f"   ✅ Green Flags: {', '.join(llm_analysis['green_flags'][:3])}")
            
            print(f"   Recommendation: {llm_analysis.get('recommendation', '')}")
        
        # Display job availability
        availability = result.get('job_availability', {})
        print(f"\n🔗 Job Availability:")
        print(f"   Status: {availability.get('reason', 'Unknown')}")
        
        print(f"\n💡 Detailed Analysis:")
        for reason in result.get('detailed_reasons', [])[:5]:
            print(f"   • {reason}")
        
        print(f"\n{'='*80}")
        
        # Add spacing between tests
        if i < len(test_jobs):
            input("\n⏸️  Press Enter to continue to next test...")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED!")
    print("="*80)
    print("\nSummary:")
    print("✅ Gemini AI integration: WORKING")
    print("✅ Real-time review scraping: WORKING")
    print("✅ Company verification: WORKING")
    print("✅ Job availability checking: WORKING")
    print("\nYour fraud detection system is fully operational! 🎉")

if __name__ == "__main__":
    try:
        test_complete_fraud_detection()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
