module Jekyll
  module FrontMatterJsonify
    def reports_jsonify(collection_item)
      # These are keys defined by Jekyll that don't mean anything to analytics-reporter
      keys_to_ignore = [
        'next', 'previous', 'path', 'id', 'output', 'content', 'to_s',
        'relative_path', 'url', 'collection', 'excerpt', 'draft', 'categories',
        'title', 'slug', 'ext', 'tags', 'date'
      ]
      results = {}

      collection_item.keys.each do |key|
        if not keys_to_ignore.include? key
          results[key] = collection_item[key]
        end
      end

      results.to_json
    end
  end
end

Liquid::Template.register_filter(Jekyll::FrontMatterJsonify)