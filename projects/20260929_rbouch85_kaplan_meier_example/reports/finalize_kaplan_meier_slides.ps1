param(
    [string]$PresentationPath = (Join-Path (Split-Path -Parent $PSScriptRoot) "outputs\reports\kaplan_meier_teaching_slides.pptx"),
    [string]$FigurePath = (Join-Path (Split-Path -Parent $PSScriptRoot) "outputs\figures\waltons_kaplan_meier.png")
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $PresentationPath -PathType Leaf)) {
    throw "PowerPoint file not found: $PresentationPath"
}
if (-not (Test-Path -LiteralPath $FigurePath -PathType Leaf)) {
    throw "Saved Kaplan-Meier figure not found: $FigurePath"
}

$presentationPath = (Resolve-Path -LiteralPath $PresentationPath).Path
$figurePath = (Resolve-Path -LiteralPath $FigurePath).Path
$workDir = Join-Path ([System.IO.Path]::GetTempPath()) ("km-pptx-" + [guid]::NewGuid().ToString("N"))
$unpackedDir = Join-Path $workDir "package"
$temporaryPresentation = Join-Path $workDir "finalized.pptx"
$description = "Kaplan-Meier survival estimates by genotype. The x-axis is days since birth; shaded bands are 95% confidence intervals, plus signs mark right-censored observations, and the at-risk counts are shown below the plot."

Add-Type -AssemblyName System.IO.Compression.FileSystem
try {
    [System.IO.Directory]::CreateDirectory($unpackedDir) | Out-Null
    [System.IO.Compression.ZipFile]::ExtractToDirectory($presentationPath, $unpackedDir)

    $namespaces = [System.Xml.XmlNamespaceManager]::new((New-Object System.Xml.NameTable))
    $namespaces.AddNamespace("a", "http://schemas.openxmlformats.org/drawingml/2006/main")
    $namespaces.AddNamespace("p", "http://schemas.openxmlformats.org/presentationml/2006/main")

    $presentationXml = [System.Xml.XmlDocument]::new()
    $presentationXml.Load((Join-Path $unpackedDir "ppt\presentation.xml"))
    $slideSize = $presentationXml.SelectSingleNode("/p:presentation/p:sldSz", $namespaces)
    if ($null -eq $slideSize) {
        throw "PowerPoint slide dimensions were not found."
    }
    $slideWidth = [double]$slideSize.GetAttribute("cx")
    $slideHeight = [double]$slideSize.GetAttribute("cy")

    $pngHeader = [byte[]]::new(24)
    $figureStream = [System.IO.File]::OpenRead($figurePath)
    try {
        if ($figureStream.Read($pngHeader, 0, $pngHeader.Length) -ne $pngHeader.Length) {
            throw "Unable to read the saved PNG dimensions."
        }
    } finally {
        $figureStream.Dispose()
    }
    $figureWidth = [double](([uint32]$pngHeader[16] -shl 24) -bor ([uint32]$pngHeader[17] -shl 16) -bor ([uint32]$pngHeader[18] -shl 8) -bor [uint32]$pngHeader[19])
    $figureHeight = [double](([uint32]$pngHeader[20] -shl 24) -bor ([uint32]$pngHeader[21] -shl 16) -bor ([uint32]$pngHeader[22] -shl 8) -bor [uint32]$pngHeader[23])
    if ($figureWidth -le 0 -or $figureHeight -le 0) {
        throw "The saved figure has invalid PNG dimensions."
    }

    $slideDirectory = Join-Path $unpackedDir "ppt\slides"
    $foundFigure = $false
    foreach ($slideFile in Get-ChildItem -LiteralPath $slideDirectory -Filter "slide*.xml" -File) {
        $slideXml = [System.Xml.XmlDocument]::new()
        $slideXml.PreserveWhitespace = $true
        $slideXml.Load($slideFile.FullName)
        $picture = $slideXml.SelectSingleNode("//p:pic[p:nvPicPr/p:cNvPr[contains(@descr, 'waltons_kaplan_meier.png')] or p:nvPicPr/p:cNvPr/@descr = '" + $description + "']", $namespaces)
        if ($null -eq $picture) {
            continue
        }
        if ($foundFigure) {
            throw "More than one slide contains the saved Kaplan-Meier figure."
        }
        $foundFigure = $true

        $pictureProperties = $picture.SelectSingleNode("p:nvPicPr/p:cNvPr", $namespaces)
        $pictureProperties.SetAttribute("descr", $description)

        $slideTree = $slideXml.SelectSingleNode("/p:sld/p:cSld/p:spTree", $namespaces)
        foreach ($shape in @($slideTree.SelectNodes("p:sp", $namespaces))) {
            [void]$slideTree.RemoveChild($shape)
        }

        $transform = $picture.SelectSingleNode("p:spPr/a:xfrm", $namespaces)
        if ($null -eq $transform) {
            throw "Figure placement data was not found in $($slideFile.Name)."
        }
        $offset = $transform.SelectSingleNode("a:off", $namespaces)
        $extent = $transform.SelectSingleNode("a:ext", $namespaces)
        if ($null -eq $offset -or $null -eq $extent) {
            throw "Figure placement data was not found in $($slideFile.Name)."
        }

        $margin = 0.18 * 914400
        $scale = [Math]::Min(($slideWidth - 2 * $margin) / $figureWidth, ($slideHeight - 2 * $margin) / $figureHeight)
        $pictureWidth = [Math]::Round($figureWidth * $scale)
        $pictureHeight = [Math]::Round($figureHeight * $scale)
        $offset.SetAttribute("x", [string][long][Math]::Round(($slideWidth - $pictureWidth) / 2))
        $offset.SetAttribute("y", [string][long][Math]::Round(($slideHeight - $pictureHeight) / 2))
        $extent.SetAttribute("cx", [string][long]$pictureWidth)
        $extent.SetAttribute("cy", [string][long]$pictureHeight)

        $slideXml.Save($slideFile.FullName)
    }

    if (-not $foundFigure) {
        throw "The saved Kaplan-Meier figure was not found in the PowerPoint."
    }

    [System.IO.Compression.ZipFile]::CreateFromDirectory(
        $unpackedDir,
        $temporaryPresentation,
        [System.IO.Compression.CompressionLevel]::Optimal,
        $false
    )
    Move-Item -LiteralPath $temporaryPresentation -Destination $presentationPath -Force
} finally {
    if (Test-Path -LiteralPath $workDir) {
        Remove-Item -LiteralPath $workDir -Recurse -Force
    }
}

Write-Output "Finalized figure placement and accessibility text in $presentationPath"
