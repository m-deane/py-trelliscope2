// Inspect React component props for country filter
const input = document.querySelector('[data-testid="filter-cat-input"]');

if (!input) {
    console.error('❌ Filter input not found!');
    console.log('Make sure the filter panel is OPEN and a country filter is visible.');
    console.log('Looking for alternative elements...');

    // Try to find the histogram directly
    const histogramBars = document.querySelectorAll('._catHistogramBar_9bydy_4');
    console.log(`Found ${histogramBars.length} histogram bars`);

    if (histogramBars.length > 0) {
        const firstBar = histogramBars[0];
        const key = Object.keys(firstBar).find(k => k.startsWith('__react'));
        if (key) {
            console.log('\n=== HISTOGRAM BAR INSPECTION ===');
            const fiber = firstBar[key];

            // Walk up the tree
            let current = fiber;
            let depth = 0;
            while (current && depth < 20) {
                const p = current.memoizedProps;
                if (p && Object.keys(p).length > 0) {
                    console.log(`\nDepth ${depth}:`);
                    console.log('  Type:', current.type?.name || current.type || 'unknown');
                    console.log('  Props keys:', Object.keys(p));

                    // Check for interesting props
                    if (p.metadata || p.meta || p.cogInfo || p.levels || p.metaVar || p.variable || p.data) {
                        console.log('  ⭐ HAS METADATA/DATA!');
                        console.log('  Details:', {
                            metadata: p.metadata,
                            meta: p.meta,
                            cogInfo: p.cogInfo,
                            levels: p.levels,
                            metaVar: p.metaVar,
                            variable: p.variable,
                            data: p.data
                        });
                    }
                }
                current = current.return;
                depth++;
            }
        }
    }
} else {
    console.log('✓ Filter input found!');
    const container = input.closest('._filterInput_1ufxt_1');
    const key = Object.keys(container).find(k => k.startsWith('__react'));

    if (key) {
    const fiber = container[key];
    const props = fiber?.return?.memoizedProps;

        console.log('=== FILTER COMPONENT PROPS ===');
        console.log('Value object:', props.value);

        // Look for metadata in parent components
        let current = fiber.return;
        let depth = 0;
        while (current && depth < 15) {
            const p = current.memoizedProps;
            if (p) {
                const hasMetadata = p.metadata || p.meta || p.cogInfo || p.levels || p.metaVar || p.variable;
                if (hasMetadata) {
                    console.log('');
                    console.log(`=== Found metadata at depth ${depth} ===`);
                    console.log('Component type:', current.type?.name || current.type);
                    console.log('Props keys:', Object.keys(p));
                    console.log('Metadata:', {
                        metadata: p.metadata,
                        meta: p.meta,
                        cogInfo: p.cogInfo,
                        levels: p.levels,
                        metaVar: p.metaVar,
                        variable: p.variable
                    });
                }
            }
            current = current.return;
            depth++;
        }
    }
}

console.log('');
console.log('=== INSPECTION COMPLETE ===');
