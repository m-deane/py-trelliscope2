// Deep inspection - walk up from histogram bar to find metadata
console.log('=== DEEP REACT TREE INSPECTION ===\n');

const histogramBars = document.querySelectorAll('._catHistogramBar_9bydy_4');
console.log(`Found ${histogramBars.length} histogram bars`);

if (histogramBars.length > 0) {
    const firstBar = histogramBars[0];
    const key = Object.keys(firstBar).find(k => k.startsWith('__react'));

    if (key) {
        const fiber = firstBar[key];
        let current = fiber;
        let depth = 0;

        console.log('\nWalking up React component tree...\n');

        while (current && depth < 25) {
            const p = current.memoizedProps;
            const typeName = current.type?.name || current.type?.displayName || (typeof current.type === 'string' ? current.type : 'anonymous');

            console.log(`\n[${ depth }] ${typeName}`);

            if (p && typeof p === 'object') {
                const keys = Object.keys(p);
                console.log(`  Props (${keys.length}):`, keys.slice(0, 10).join(', '));

                // Check for metadata-related props
                const metaKeys = keys.filter(k =>
                    k.includes('meta') ||
                    k.includes('level') ||
                    k.includes('cog') ||
                    k.includes('data') ||
                    k.includes('variable') ||
                    k.includes('filter')
                );

                if (metaKeys.length > 0) {
                    console.log('  ⭐ METADATA-RELATED PROPS:', metaKeys);
                    metaKeys.forEach(mk => {
                        const val = p[mk];
                        if (val && typeof val === 'object') {
                            console.log(`    ${mk}:`, Object.keys(val).slice(0, 5));
                            // If it looks like it has levels, show them
                            if (val.levels && Array.isArray(val.levels)) {
                                console.log(`      📊 levels (${val.levels.length}):`, val.levels.slice(0, 3));
                            }
                        } else {
                            console.log(`    ${mk}:`, val);
                        }
                    });
                }

                // Specifically look for cogInfo structure
                if (p.cogInfo) {
                    console.log('  🎯 FOUND cogInfo!');
                    console.log('    Keys:', Object.keys(p.cogInfo));
                    if (p.cogInfo.country) {
                        console.log('    country:', p.cogInfo.country);
                    }
                }

                // Look for displayInfo
                if (p.displayInfo) {
                    console.log('  🎯 FOUND displayInfo!');
                    if (p.displayInfo.cogInfo) {
                        console.log('    Has cogInfo:', Object.keys(p.displayInfo.cogInfo));
                    }
                }
            }

            current = current.return;
            depth++;
        }

        console.log('\n=== TREE WALK COMPLETE ===');
    }
} else {
    console.error('❌ No histogram bars found! Make sure filter panel is open.');
}
