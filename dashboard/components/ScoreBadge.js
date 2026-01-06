import React from 'react';

export default function ScoreBadge({ score }) {
    let badgeClass = 'badge-red';
    if (score >= 80) badgeClass = 'badge-blue';
    else if (score >= 50) badgeClass = 'badge-yellow';
    // else red tier gets Green (Neon)

    return (
        <div className={`badge ${badgeClass} flex gap-2`}>
            <span>{score}%</span>
        </div>
    );
}
