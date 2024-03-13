function Inlines(inlines)
  for i = #inlines-1, 1, -1 do
    if inlines[i].t == "SoftBreak" then
      inlines[i] = pandoc.LineBreak()
    end
  end
  return inlines
end
