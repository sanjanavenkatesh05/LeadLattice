"use client";
import React, { useState, useMemo } from 'react';
import ScoreBadge from './ScoreBadge';

export default function LeadTable({ leads }) {
    const [search, setSearch] = useState('');
    const [sortConfig, setSortConfig] = useState({ key: 'score', direction: 'desc' });

    const filteredLeads = useMemo(() => {
        let result = [...leads];
        if (search) {
            const q = search.toLowerCase();
            result = result.filter(l =>
                l.name.toLowerCase().includes(q) ||
                l.title.toLowerCase().includes(q) ||
                l.company.name.toLowerCase().includes(q)
            );
        }

        result.sort((a, b) => {
            let aVal = a[sortConfig.key];
            let bVal = b[sortConfig.key];

            if (sortConfig.key.includes('.')) {
                const keys = sortConfig.key.split('.');
                aVal = a[keys[0]][keys[1]];
                bVal = b[keys[0]][keys[1]];
            }

            if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
            if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
            return 0;
        });

        return result;
    }, [leads, search, sortConfig]);

    const handleSort = (key) => {
        let direction = 'desc';
        if (sortConfig.key === key && sortConfig.direction === 'desc') {
            direction = 'asc';
        }
        setSortConfig({ key, direction });
    };

    const downloadCSV = () => {
        const headers = [
            'Rank', 'Probability', 'Name', 'Title', 'Company', 'Location HQ', 'Email', 'LinkedIn'
        ];

        const rows = filteredLeads.map((lead) => {
            return [
                lead.rank_tier,
                `${lead.score}%`,
                `"${lead.name}"`,
                `"${lead.title}"`,
                `"${lead.company.name}"`,
                `"${lead.company.location_hq}"`,
                `"${lead.email}"`,
                `"https://${lead.linkedin_url}"`
            ];
        });

        const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', 'lead_lattice_export.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="w-full">
            <div className="flex gap-4 mb-6 justify-between items-center">
                <input
                    type="text"
                    placeholder="Filter by name, title, or company..."
                    className="search-input flex-1"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
                <button onClick={downloadCSV} className="btn-primary whitespace-nowrap flex items-center gap-2">
                    <span>EXPORT EXCEL</span>
                </button>
            </div>

            <div className="glass-panel overflow-hidden">
                <div className="lead-table-container">
                    <table className="w-full text-left">
                        <thead>
                            <tr>
                                <th onClick={() => handleSort('score')} className="cursor-pointer">RANK</th>
                                <th onClick={() => handleSort('score')} className="cursor-pointer">PROBABILITY</th>
                                <th onClick={() => handleSort('name')} className="cursor-pointer">NAME</th>
                                <th onClick={() => handleSort('title')} className="cursor-pointer">TITLE</th>
                                <th onClick={() => handleSort('company.name')} className="cursor-pointer">COMPANY</th>
                                <th>LOCATION HQ</th>
                                <th>EMAIL</th>
                                <th>LINKEDIN</th>
                                <th>ACTION</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredLeads.map((lead) => {
                                return (
                                    <tr key={lead.id}>
                                        <td className="text-xs font-bold text-white uppercase">{lead.rank_tier}</td>
                                        <td><ScoreBadge score={lead.score} /></td>
                                        <td className="font-bold text-white max-w-[150px] truncate" title={lead.name}>{lead.name}</td>
                                        <td className="text-zinc-400 text-sm max-w-[150px] truncate" title={lead.title}>{lead.title}</td>
                                        <td className="text-white max-w-[150px] truncate" title={lead.company.name}>{lead.company.name}</td>
                                        <td className="text-zinc-400 text-sm">{lead.company.location_hq}</td>
                                        <td className="text-xs text-zinc-500 max-w-[120px] truncate" title={lead.email}>{lead.email}</td>
                                        <td className="text-xs text-zinc-500 max-w-[150px] truncate">
                                            {lead.linkedin_url.replace('www.linkedin.com/in/', '').replace('www.linkedin.com/search/results/all/?keywords=', 'Search: ').substring(0, 20)}...
                                        </td>
                                        <td>
                                            <a href={`https://${lead.linkedin_url}`} target="_blank" rel="noopener noreferrer" className="btn-primary py-1 px-3 text-[10px]">
                                                OPEN
                                            </a>
                                        </td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
