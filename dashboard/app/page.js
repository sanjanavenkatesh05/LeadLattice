import { promises as fs } from 'fs';
import path from 'path';
import LeadTable from '@/components/LeadTable';

async function getLeads() {
  // Simulating external data fetch by reading local JSON
  const filePath = path.join(process.cwd(), 'public', 'leads_data.json');
  const fileContents = await fs.readFile(filePath, 'utf8');
  const data = JSON.parse(fileContents);
  // The JSON file is a direct array of leads
  return Array.isArray(data) ? data : (data.leads || []);
}

export default async function Home() {
  const leads = await getLeads();

  return (
    <main className="min-h-screen p-8 max-w-7xl mx-auto">
      <div className="glass-header p-6 mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold tracking-tighter text-white">
            LEAD<span className="text-gradient">LATTICE</span>
          </h1>
          <p className="text-slate-500 mt-1 text-sm tracking-widest uppercase">
            Lead Prioritization Engine
          </p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-white bg-clip-text" style={{ textShadow: '0 0 10px rgba(255,0,127,0.5)' }}>
            {leads.length}
          </div>
          <div className="text-[10px] text-zinc-500 uppercase tracking-[0.2em]">Active Targets</div>
        </div>
      </div>

      <LeadTable leads={leads} />
    </main>
  );
}
