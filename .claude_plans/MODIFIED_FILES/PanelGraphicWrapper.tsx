/* eslint-disable react/jsx-no-useless-fragment */
import React, { useState, useEffect } from 'react';
import PanelGraphic from './PanelGraphic';
import { panelSrcGetter, replaceDatumFactorsWithLabels, snakeCase } from '../../utils';
import { useDisplayInfo } from '../../slices/displayInfoAPI';

interface PanelGraphicProps {
  data: Datum;
  meta: IPanelMeta;
  alt: string;
  imageWidth: number;
  basePath: string;
  displayName: string;
  panelKey: string;
  fileName: string;
}

const PanelGraphicWrapper: React.FC<PanelGraphicProps> = ({
  data,
  meta,
  alt,
  imageWidth,
  basePath,
  displayName = '',
  panelKey,
  fileName,
}) => {
  const { data: displayInfo } = useDisplayInfo();
  const [panelSrc, setPanelSrc] = useState<string | React.ReactElement>('');
  const sourceFunc = async (func: PanelFunction) => {
    setPanelSrc('');
    const dataWithFactorLabels = replaceDatumFactorsWithLabels(data, displayInfo?.metas as IMeta[]);
    const res = await func(dataWithFactorLabels);
    setPanelSrc(res);
    return res;
  };

  useEffect(() => {
    if (meta?.source?.type === 'JS' && meta?.source?.function) {
      sourceFunc(meta.source.function);
    }
  }, [meta, data]);

  /**
   * Build panel source URL based on source type
   * MODIFIED for Python package REST panel support
   */
  const getPanelSrc = (): string | React.ReactElement => {
    // JavaScript-based panels (existing functionality)
    if (meta?.source?.type === 'JS' && meta?.source?.function) {
      return panelSrc;
    }

    // REST API panels (NEW - Python package support)
    if (meta?.source?.type === 'REST') {
      const restSource = meta.source as IRESTPanelSource;
      return `${restSource.url}/${fileName}`;
    }

    // Non-local panels (URL provided directly)
    if (meta?.source?.isLocal === false) {
      return fileName.toString();
    }

    // Local file panels (default - existing functionality)
    return panelSrcGetter(basePath, fileName as string, snakeCase(displayName)).toString();
  };

  return (
    <PanelGraphic
      type={meta?.paneltype}
      src={getPanelSrc()}
      alt={alt}
      aspectRatio={meta?.aspect}
      imageWidth={imageWidth}
      key={panelKey}
      port={meta?.source?.port}
      sourceType={meta?.source?.type}
      name={meta?.varname}
      sourceClean={fileName}
    />
  );
};

export default PanelGraphicWrapper;
