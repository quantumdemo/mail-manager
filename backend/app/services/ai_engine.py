import re
from collections import Counter

class AIRecommendationEngine:
    @staticmethod
    def analyze_emails(emails):
        """
        Analyze emails and provide recommendations for deletion.
        """
        sender_counts = Counter(e['sender'] for e in emails)
        recommendations = {}

        # Heuristics for common bulk senders/newsletters
        bulk_keywords = ['newsletter', 'noreply', 'no-reply', 'marketing', 'info', 'offers', 'promotions', 'subscription', 'support', 'alert', 'notification']

        for email in emails:
            score = 0
            explanation = []
            sender = email['sender'].lower()
            subject = email.get('subject', '').lower()

            # 1. Frequency heuristic
            count = sender_counts[email['sender']]
            if count > 100:
                score += 40
                explanation.append(f"Extremely high frequency ({count} emails)")
            elif count > 50:
                score += 25
                explanation.append(f"High frequency sender ({count} emails)")

            # 2. Keyword heuristic in sender name/email
            matched_keywords = [k for k in bulk_keywords if k in sender]
            if matched_keywords:
                score += 35
                explanation.append(f"Sender matches bulk pattern: {matched_keywords[0]}")

            # 3. Keyword heuristic in subject
            subject_keywords = ['off', '%', 'sale', 'deal', 'limited time', 'unsubscribe', 'verify']
            matched_subject = [k for k in subject_keywords if k in subject]
            if matched_subject:
                score += 15
                explanation.append(f"Subject contains promotional keyword: {matched_subject[0]}")

            # 4. Size heuristic
            if email['size'] > 1024 * 1024 * 10: # > 10MB
                score += 30
                explanation.append("Very large email (> 10MB)")
            elif email['size'] > 1024 * 1024 * 5: # > 5MB
                score += 15
                explanation.append("Large email (> 5MB)")

            # Determine label
            if score >= 60:
                label = 'safe'
            elif score >= 30:
                label = 'review'
            else:
                label = 'keep'

            recommendations[email['id']] = {
                'label': label,
                'confidence': min(score, 100) / 100.0,
                'explanation': " | ".join(explanation) if explanation else "Low priority for deletion"
            }

        return recommendations

    @staticmethod
    def group_emails(emails):
        groups = {}
        for email in emails:
            sender = email['sender']
            if sender not in groups:
                groups[sender] = {
                    'sender': sender,
                    'count': 0,
                    'total_size': 0,
                    'emails': []
                }
            groups[sender]['count'] += 1
            groups[sender]['total_size'] += email['size']
            groups[sender]['emails'].append(email)

        # Convert to list and sort by size
        sorted_groups = sorted(groups.values(), key=lambda x: x['total_size'], reverse=True)
        return sorted_groups
